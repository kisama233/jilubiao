<template>
  <div class="markdown-view">
    <el-card class="page-card" shadow="never">
      <MarkdownEditor />
    </el-card>
  </div>
</template>

<script>
import MarkdownEditor from '@/components/MarkdownEditor.vue'

export default {
  name: 'MarkdownView',
  components: {
    MarkdownEditor
  }
}
</script>

<style scoped>
.markdown-view {
  padding: 20px;
  height: calc(100vh - 60px);
}
.page-card {
  height: 100%;
}
</style>