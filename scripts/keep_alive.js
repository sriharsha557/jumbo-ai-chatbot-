// Keep Render backend alive by pinging it every 14 minutes
// Run this on a free service like GitHub Actions or Vercel Edge Functions

const BACKEND_URL = 'https://hellojumbo.onrender.com/health';
const PING_INTERVAL = 14 * 60 * 1000; // 14 minutes

async function pingBackend() {
    try {
        const response = await fetch(BACKEND_URL);
        const timestamp = new Date().toISOString();
        
        if (response.ok) {
            console.log(`✅ ${timestamp}: Backend is alive`);
        } else {
            console.log(`⚠️ ${timestamp}: Backend responded with ${response.status}`);
        }
    } catch (error) {
        console.log(`❌ ${timestamp}: Failed to ping backend:`, error.message);
    }
}

// Ping immediately and then every 14 minutes
pingBackend();
setInterval(pingBackend, PING_INTERVAL);

console.log('🚀 Keep-alive service started. Pinging every 14 minutes...');