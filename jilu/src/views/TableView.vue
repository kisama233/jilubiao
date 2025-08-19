<template>
  <div class="table-view">
    <el-card class="page-card" shadow="never">
      <RecordTable />
    </el-card>
  </div>
</template>

<script>
import RecordTable from '@/components/RecordTable.vue'

export default {
  name: 'TableView',
  components: {
    RecordTable
  }
}
</script>

<style scoped>
.table-view {
  padding: 20px;
}
.page-card {
  min-height: calc(100vh - 120px);
}
</style>