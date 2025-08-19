<template>
  <div class="record-table">
    <div class="toolbar">
      <el-button type="primary" @click="showAddDialog">添加记录</el-button>
      <el-button @click="refreshTable">刷新</el-button>
    </div>

    <div class="table-scroll">
      <el-table :data="tableData" height="100%" border style="width: 100%">
        <el-table-column prop="date" label="日期" width="180" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="content" label="内容" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === '完成' ? 'success' : 'warning'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(scope.$index, scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
      <el-form :model="form" label-width="80px">
        <el-form-item label="日期">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" rows="4" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="进行中" value="进行中" />
            <el-option label="完成" value="完成" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'RecordTable',
  setup() {
    const tableData = ref([])
    const dialogVisible = ref(false)
    const dialogTitle = ref('添加记录')
    const form = ref({
      id: null,
      date: '',
      title: '',
      content: '',
      status: '进行中'
    })
    const isEdit = ref(false)
    const tableLoading = ref(false)

    const showAddDialog = () => {
      resetForm()
      dialogTitle.value = '添加记录'
      isEdit.value = false
      dialogVisible.value = true
    }

    const handleEdit = (_index, row) => {
      void _index
      form.value = { ...row }
      dialogTitle.value = '编辑记录'
      isEdit.value = true
      dialogVisible.value = true
    }

    const handleDelete = (_index, _row) => {
      void _index
      void _row
      if (!_row?.id) return
      axios
        .delete(`http://localhost:5000/api/delete-record/${_row.id}`)
        .then(() => {
          ElMessage.success('删除成功')
          refreshTable()
        })
        .catch(() => {
          ElMessage.error('删除失败')
        })
    }

    const submitForm = async () => {
      if (!form.value.date || !form.value.title) {
        ElMessage.error('请填写日期与标题')
        return
      }
      try {
        if (isEdit.value && form.value.id) {
          await axios.put(`http://localhost:5000/api/update-record/${form.value.id}` , {
            date: form.value.date,
            title: form.value.title,
            content: form.value.content,
            status: form.value.status
          })
          ElMessage.success('更新成功')
        } else {
          await axios.post('http://localhost:5000/api/add-record', {
            date: form.value.date,
            title: form.value.title,
            content: form.value.content,
            status: form.value.status
          })
          ElMessage.success('新增成功')
        }
        dialogVisible.value = false
        refreshTable()
      } catch (e) {
        ElMessage.error('提交失败')
      }
    }

    const refreshTable = async () => {
      tableLoading.value = true
      try {
        const { data } = await axios.get('http://localhost:5000/api/get-records')
        tableData.value = data?.data || []
      } catch (e) {
        ElMessage.error('获取数据失败')
      } finally {
        tableLoading.value = false
      }
    }

    const resetForm = () => {
      form.value = {
        id: null,
        date: '',
        title: '',
        content: '',
        status: '进行中'
      }
    }

    onMounted(() => {
      refreshTable()
    })

    return {
      tableData,
      dialogVisible,
      dialogTitle,
      form,
      showAddDialog,
      handleEdit,
      handleDelete,
      submitForm,
      refreshTable,
      tableLoading
    }
  }
})
</script>

<style scoped>
.record-table {
  padding: 20px;
}
.toolbar {
  margin-bottom: 20px;
}
.table-scroll {
  height: calc(100vh - 260px);
  min-height: 360px;
  overflow: hidden;
}
</style>