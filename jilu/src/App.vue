<template>
  <div id="app">
    <el-container style="min-height: 100vh;">
      <el-header height="56px">
        <div class="topbar">
          <div class="brand">记录应用</div>
          <div class="nav-links">
            <router-link to="/">首页</router-link>
            <router-link to="/markdown">Markdown</router-link>
            <router-link to="/table">记录表</router-link>
            <router-link to="/about">关于</router-link>
            <el-divider direction="vertical" />
            <el-switch
              v-model="isDark"
              inline-prompt
              active-text="暗黑"
              inactive-text="明亮"
              @change="toggleDark"
            />
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
  
</template>

<script>
export default {
  name: 'AppRoot',
  data() {
    return { isDark: false }
  },
  mounted() {
    // 从本地存储恢复主题
    const saved = localStorage.getItem('prefers-dark')
    if (saved === '1') {
      this.isDark = true
      document.documentElement.classList.add('dark')
    }
  },
  methods: {
    toggleDark() {
      if (this.isDark) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('prefers-dark', '1')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('prefers-dark', '0')
      }
    }
  }
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, PingFang SC, Microsoft YaHei, WenQuanYi Micro Hei, sans-serif;
  color: #303133;
  background: radial-gradient(1200px 600px at 20% -10%, #eef4ff 0%, transparent 60%),
              radial-gradient(1000px 500px at 110% 10%, #f5faff 0%, transparent 60%),
              linear-gradient(180deg, #fafafa, #ffffff);
  min-height: 100vh;
}
.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  font-weight: 600;
}
.nav-links a {
  margin-left: 16px;
  color: #606266;
  text-decoration: none;
}
.nav-links a.router-link-exact-active {
  color: #409EFF;
}

/* 暗黑模式下略微压暗背景 */
:root.dark #app {
  background: linear-gradient(180deg, #0b0c10, #0f1115);
  color: #e5e7eb;
}
</style>
