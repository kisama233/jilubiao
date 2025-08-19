<template>
  <div class="home">
    <div class="hero">
      <h1>记录应用 · 主界面</h1>
      <p class="subtitle">选择要进入的功能页面</p>
    </div>
    <div class="actions">
      <router-link to="/markdown">
        <el-button class="dark-btn" size="large">Markdown 撰写</el-button>
      </router-link>
      <router-link to="/table">
        <el-button class="dark-btn" size="large">记录表</el-button>
      </router-link>
      <router-link to="/about">
        <el-button class="dark-btn" size="large">关于</el-button>
      </router-link>
    </div>
  </div>
  
</template>

<script>
export default {
  name: 'HomeView'
}
</script>
 .home {
   min-height: calc(100vh - 60px);
   display: flex;
   flex-direction: column;
   align-items: center;
   justify-content: center;
   padding: 20px;
 }
 .hero {
   text-align: center;
   margin-bottom: 24px;
 }
 .subtitle {
   color: #777;
   margin-top: 8px;
 }
 .actions {
   display: flex;
   gap: 16px;
 }
 .dark-btn {
   background: #1f2937;
   border-color: #1f2937;
   color: #ffffff;
 }
 .dark-btn:hover, .dark-btn:focus {
   background: #111827;
   border-color: #111827;
   color: #ffffff;
 }
 .dark-btn.is-disabled {
   background: #374151;
   border-color: #374151;
   color: #d1d5db;
 }