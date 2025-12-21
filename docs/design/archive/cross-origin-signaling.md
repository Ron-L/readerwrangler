# Cross-Origin Signaling for Browser-Based Data Sync

A lightweight solution for signaling data freshness between JavaScript running on two different domains, without requiring the user to interact with a file picker.

## The Problem

You have:
- **Source domain**: A bookmarklet (or userscript) that fetches data and saves a JSON file to the user's disk
- **Sink domain**: A web app (e.g., on GitHub Pages) that reads that JSON file via the File Picker API

The Sink app can detect staleness by checking a timestamp embedded in the JSON file. But it has no way to know when the Source has fetched *newer* data—polling the file would require repeated user interaction with the file picker.

## The Solution

Use a tiny signaling backend that both sides can talk to:

1. **Source side** (bookmarklet): After saving new data, POST a version/timestamp to the backend
2. **Sink side** (your app): Periodically poll the backend to check if a newer version exists
3. **Channel ID**: A unique identifier (UUID) that links a specific user's Source and Sink

```
┌─────────────────┐         ┌─────────────────┐
│  Source Domain  │         │   Sink Domain   │
│  (bookmarklet)  │         │  (GitHub Pages) │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ POST /update/:channelId   │ GET /check/:channelId
         │                           │
         └──────────┐     ┌──────────┘
                    │     │
                    ▼     ▼
              ┌─────────────────┐
              │ Signaling API   │
              │ (Cloudflare/    │
              │  Deno/etc.)     │
              └─────────────────┘
```

---

## Backend Implementation

### Option A: Cloudflare Workers + KV (Recommended)

**Why Cloudflare?**
- 100,000 requests/day free tier
- KV storage included (1GB free)
- Global edge deployment
- No cold starts

#### 1. Setup

1. Create a Cloudflare account at https://cloudflare.com
2. Go to **Workers & Pages** → **Create Worker**
3. Create a KV namespace:
   - Go to **Workers & Pages** → **KV**
   - Create namespace called `SIGNAL_STORE`
4. Bind the KV namespace to your worker:
   - In your worker settings → **Variables and Secrets** → **KV Namespace Bindings**
   - Variable name: `SIGNAL_STORE`, select your namespace

#### 2. Worker Code

```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers for cross-origin requests
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Route: POST /update/:channelId
    const updateMatch = path.match(/^\/update\/([a-zA-Z0-9-]+)$/);
    if (updateMatch && request.method === 'POST') {
      const channelId = updateMatch[1];
      const body = await request.json();
      const version = body.version || Date.now();
      
      await env.SIGNAL_STORE.put(channelId, JSON.stringify({
        version,
        updatedAt: new Date().toISOString()
      }), {
        expirationTtl: 60 * 60 * 24 * 30  // 30 days
      });
      
      return new Response(JSON.stringify({ ok: true, version }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }
    
    // Route: GET /check/:channelId
    const checkMatch = path.match(/^\/check\/([a-zA-Z0-9-]+)$/);
    if (checkMatch && request.method === 'GET') {
      const channelId = checkMatch[1];
      const data = await env.SIGNAL_STORE.get(channelId);
      
      if (!data) {
        return new Response(JSON.stringify({ version: null }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
      
      return new Response(data, {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }
    
    // 404 for everything else
    return new Response('Not Found', { status: 404, headers: corsHeaders });
  }
};
```

#### 3. Deploy

Click **Deploy** in the Cloudflare dashboard. Your API will be live at:
```
https://your-worker-name.your-subdomain.workers.dev
```

---

### Option B: Deno Deploy + Deno KV

**Why Deno Deploy?**
- 1,000,000 requests/month free tier
- Built-in KV database (no setup)
- Simple deployment from GitHub

#### 1. Setup

1. Create account at https://deno.com/deploy
2. Create new project, link to a GitHub repo (or use the playground)

#### 2. Code

```typescript
const kv = await Deno.openKv();

Deno.serve(async (request) => {
  const url = new URL(request.url);
  const path = url.pathname;
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
  
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }
  
  // POST /update/:channelId
  const updateMatch = path.match(/^\/update\/([a-zA-Z0-9-]+)$/);
  if (updateMatch && request.method === 'POST') {
    const channelId = updateMatch[1];
    const body = await request.json();
    const version = body.version || Date.now();
    
    await kv.set(['signals', channelId], {
      version,
      updatedAt: new Date().toISOString()
    }, { expireIn: 30 * 24 * 60 * 60 * 1000 }); // 30 days
    
    return Response.json({ ok: true, version }, { headers: corsHeaders });
  }
  
  // GET /check/:channelId
  const checkMatch = path.match(/^\/check\/([a-zA-Z0-9-]+)$/);
  if (checkMatch && request.method === 'GET') {
    const channelId = checkMatch[1];
    const result = await kv.get(['signals', channelId]);
    
    return Response.json(result.value || { version: null }, { headers: corsHeaders });
  }
  
  return new Response('Not Found', { status: 404, headers: corsHeaders });
});
```

---

## Client-Side Implementation

### Sink App (Your GitHub Pages App)

#### Channel ID Management

Generate and store a unique channel ID for each user:

```javascript
function getOrCreateChannelId() {
  let channelId = localStorage.getItem('signalChannelId');
  if (!channelId) {
    channelId = crypto.randomUUID();
    localStorage.setItem('signalChannelId', channelId);
  }
  return channelId;
}
```

#### Check for Updates

```javascript
const SIGNAL_API = 'https://your-worker.workers.dev';

async function checkForUpdates(localVersion) {
  const channelId = getOrCreateChannelId();
  
  try {
    const response = await fetch(`${SIGNAL_API}/check/${channelId}`);
    const data = await response.json();
    
    if (data.version && data.version > localVersion) {
      return {
        hasUpdate: true,
        remoteVersion: data.version,
        updatedAt: data.updatedAt
      };
    }
    
    return { hasUpdate: false };
  } catch (error) {
    console.warn('Signal check failed:', error);
    return { hasUpdate: false, error };
  }
}
```

#### Polling (Optional)

```javascript
function startPolling(localVersion, onUpdateAvailable, intervalMs = 60000) {
  const check = async () => {
    const result = await checkForUpdates(localVersion);
    if (result.hasUpdate) {
      onUpdateAvailable(result);
    }
  };
  
  check(); // Initial check
  return setInterval(check, intervalMs);
}

// Usage
const stopPolling = startPolling(
  myCurrentDataVersion,
  (update) => {
    showNotification(`New data available (updated ${update.updatedAt})`);
  },
  5 * 60 * 1000  // Check every 5 minutes
);
```

#### UI for Channel ID

Users need to copy their channel ID to configure the bookmarklet:

```javascript
function renderChannelIdUI() {
  const channelId = getOrCreateChannelId();
  
  return `
    <div class="channel-config">
      <p>Your sync channel ID:</p>
      <code id="channel-id">${channelId}</code>
      <button onclick="navigator.clipboard.writeText('${channelId}')">
        Copy
      </button>
      <p class="help-text">
        Add this to your bookmarklet to enable update notifications.
      </p>
    </div>
  `;
}
```

---

### Source Side (Bookmarklet)

The bookmarklet needs the channel ID and API URL configured. Here's a template:

```javascript
javascript:(function(){
  /* === CONFIGURATION === */
  const SIGNAL_API = 'https://your-worker.workers.dev';
  const CHANNEL_ID = 'PASTE_YOUR_CHANNEL_ID_HERE';
  
  /* === YOUR EXISTING BOOKMARKLET CODE === */
  // ... fetch data, process it, save file ...
  const dataVersion = Date.now();
  
  // After saving the file, signal the update
  fetch(`${SIGNAL_API}/update/${CHANNEL_ID}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ version: dataVersion })
  }).then(() => {
    console.log('Signaled update:', dataVersion);
  }).catch((err) => {
    console.warn('Signal failed (non-critical):', err);
  });
})();
```

#### Bookmarklet Generator

You could add a generator to your Sink app that creates a ready-to-use bookmarklet:

```javascript
function generateBookmarklet(channelId, signalApi) {
  const code = `
    javascript:(function(){
      const SIGNAL_API='${signalApi}';
      const CHANNEL_ID='${channelId}';
      
      /* User's existing logic would go here */
      
      const version=Date.now();
      fetch(SIGNAL_API+'/update/'+CHANNEL_ID,{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({version})
      });
    })();
  `.replace(/\s+/g, ' ').trim();
  
  return code;
}
```

---

## Complete Integration Example

### Sink App Integration

```javascript
class DataSyncManager {
  constructor(signalApi) {
    this.signalApi = signalApi;
    this.channelId = this.getOrCreateChannelId();
    this.localVersion = null;
    this.pollInterval = null;
  }
  
  getOrCreateChannelId() {
    let id = localStorage.getItem('signalChannelId');
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem('signalChannelId', id);
    }
    return id;
  }
  
  // Called when user loads a file via file picker
  onFileLoaded(jsonData) {
    // Assuming your JSON has a timestamp field
    this.localVersion = jsonData.exportedAt || jsonData.timestamp;
    this.startPolling();
  }
  
  async checkForUpdates() {
    if (!this.localVersion) return { hasUpdate: false };
    
    try {
      const res = await fetch(`${this.signalApi}/check/${this.channelId}`);
      const data = await res.json();
      
      return {
        hasUpdate: data.version && data.version > this.localVersion,
        remoteVersion: data.version,
        localVersion: this.localVersion
      };
    } catch (e) {
      return { hasUpdate: false, error: e };
    }
  }
  
  startPolling(intervalMs = 300000) { // 5 minutes
    this.stopPolling();
    
    const poll = async () => {
      const result = await this.checkForUpdates();
      if (result.hasUpdate) {
        this.onUpdateAvailable(result);
      }
    };
    
    poll();
    this.pollInterval = setInterval(poll, intervalMs);
  }
  
  stopPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }
  
  onUpdateAvailable(result) {
    // Override this or dispatch an event
    const event = new CustomEvent('data-update-available', { detail: result });
    window.dispatchEvent(event);
  }
  
  getChannelId() {
    return this.channelId;
  }
}

// Usage
const syncManager = new DataSyncManager('https://your-worker.workers.dev');

window.addEventListener('data-update-available', (e) => {
  document.getElementById('update-banner').hidden = false;
  document.getElementById('update-banner').textContent = 
    'Newer data is available! Use the file picker to load the latest export.';
});
```

---

## Security Considerations

1. **Channel IDs are unguessable**: UUIDs provide sufficient entropy that users can't stumble onto each other's channels.

2. **No sensitive data transmitted**: Only timestamps/version numbers flow through the signal API—the actual data still goes through the user's filesystem.

3. **Optional: Add rate limiting**: The Cloudflare/Deno examples above are minimal. For production, consider adding rate limiting per channel ID.

4. **Optional: Channel expiration**: The examples set a 30-day TTL. Inactive channels auto-delete.

---

## Cost Estimation

For a user base of dozens to low thousands:

| Usage Pattern | Requests/Month | Cloudflare | Deno Deploy |
|---------------|----------------|------------|-------------|
| 100 users, hourly polls | ~72,000 | Free | Free |
| 500 users, 5-min polls | ~4.3M | ~$5/mo | Free |
| 1000 users, 5-min polls | ~8.6M | ~$5/mo | ~$10/mo |

For your expected scale (dozens to hundreds), you'll almost certainly stay within free tiers.

---

## Summary

This approach gives you:
- Real-time(ish) staleness detection without user interaction
- No changes needed to the source domain's server
- Minimal backend (~20 lines of code)
- Free hosting for your expected scale
- Easy user setup (just copy/paste a channel ID)

The main tradeoff is that users need to configure their bookmarklet with their channel ID, but this is a one-time setup step.
