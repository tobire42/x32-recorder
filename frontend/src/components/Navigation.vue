<template>
  <nav class="nav-bar">
    <div class="nav-container">
      <div class="nav-brand">
        <h1>🎙️ X32 Recorder</h1>
      </div>
      <div class="nav-links">
        <router-link to="/recorder" class="nav-link" active-class="active">
          Recorder
        </router-link>
        <router-link to="/templates" class="nav-link" active-class="active">
          Templates
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navigation'
}
</script>

<style scoped>
.nav-bar {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand h1 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-link {
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-link.active {
  background: white;
  color: #667eea;
}
</style>
