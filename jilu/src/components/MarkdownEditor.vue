<template>
  <div class="markdown-editor">
    <div class="toolbar">
      <el-button-group>
        <el-button @click="insertText('**', '**')">加粗</el-button>
        <el-button @click="insertText('*', '*')">斜体</el-button>
        <el-button @click="insertText('# ', '')">标题</el-button>
        <el-button @click="insertText('- ', '')">列表</el-button>
        <el-button @click="insertText('[', '](url)')">链接</el-button>
      </el-button-group>
      <el-button-group>
        <el-input v-model="currentFilename" placeholder="文件名（.md）" style="width: 240px" />
        <el-button @click="saveDocument">保存</el-button>
        <el-button @click="fetchFileList">刷新列表</el-button>
        <el-button @click="exportDocument">导出</el-button>
        <el-button @click="triggerImport">导入文件</el-button>
        <el-button @click="triggerInsertImage">插入图片</el-button>
        <el-button @click="openImageDialog">插入已有图片</el-button>
      </el-button-group>
    </div>
    <div class="editor-container">
      <div class="sidebar" :style="{ width: sidebarCollapsed ? '12px' : '260px' }">
        <div class="sidebar-toggle" @click="toggleSidebar" :title="sidebarCollapsed ? '展开侧栏' : '折叠侧栏'">
          {{ sidebarCollapsed ? '›' : '‹' }}
        </div>
        <div v-if="!sidebarCollapsed" class="sidebar-header">
          <el-input v-model="searchQuery" placeholder="搜索文件" clearable />
          <div class="sidebar-actions">
            <el-button size="small" @click="newDocument">新建</el-button>
            <el-button size="small" @click="fetchFileList">刷新</el-button>
          </div>
        </div>
        <div v-if="!sidebarCollapsed" class="sidebar-list">
          <div
            v-for="item in filteredFiles"
            :key="item.name"
            class="file-item"
            :class="{ active: item.name === currentFilename }"
            @click="loadExistingDocument(item.name)"
          >
            <span class="file-icon">{{ getFileIcon(item.name) }}</span>
            <span class="file-name">{{ item.name }}</span>
            <el-button link type="primary" size="small" @click.stop="renameDocument(item.name)">重命名</el-button>
            <el-button link type="danger" size="small" @click.stop="removeDocument(item.name)">删除</el-button>
          </div>
        </div>
      </div>
      <div class="editor-pane" :style="{ width: editorWidth + '%' }">
        <div class="pane-header">
          <div class="pane-tools">
            <el-button size="small" @click="toggleEditorExpand" title="放大/还原编辑">⤢</el-button>
          </div>
        </div>
        <el-input
          class="editor-textarea"
          type="textarea"
          v-model="markdownText"
          placeholder="输入Markdown内容..."
          resize="none"
          rows="20"
        />
      </div>
      <div class="divider" @mousedown="startDrag"></div>
      <div class="preview-pane" :style="{ width: (100 - editorWidth) + '%' }">
        <div class="preview-header">
          <div class="preview-tools">
            <el-button size="small" @click="scrollPreview('up')" title="向上滚动">↑</el-button>
            <el-button size="small" @click="scrollPreview('down')" title="向下滚动">↓</el-button>
            <span class="label">图片大小</span>
            <el-slider v-model="imageWidthPercent" :min="20" :max="200" :show-tooltip="false" style="width: 160px" />
            <span class="label">文字缩放</span>
            <el-slider v-model="previewZoom" :min="20" :max="200" :show-tooltip="false" style="width: 160px" />
            <el-button size="small" @click="toggleExpand" title="放大/还原预览">⤢</el-button>
          </div>
        </div>
        <div class="preview-content" ref="previewRef" :style="{'--img-max-width': imageWidthPercent + '%', '--preview-zoom': (previewZoom/100)}">
          <template v-if="pdfPreviewUrl">
            <iframe class="pdf-frame" :src="pdfPreviewUrl" @dblclick="openPdfDialog"></iframe>
          </template>
          <template v-else>
            <div v-html="compiledMarkdown"></div>
          </template>
          <div
            v-show="showImgHandle"
            class="img-resize-handle"
            :style="{ left: imgHandleLeft + 'px', top: imgHandleTop + 'px' }"
            @mousedown.stop="startImageResize"
            title="拖拽调整图片大小"
          />
        </div>
      </div>
    </div>
    
    <input
      ref="fileInputRef"
      type="file"
      accept=".md,.txt,.pdf,.jpg,.jpeg,.png,.gif"
      style="display:none"
      @change="handleFileChange"
    />
    
    <input
      ref="imageInputRef"
      type="file"
      accept="image/*"
      style="display:none"
      @change="handleImageChange"
    />
    
    <el-dialog v-model="listDialogVisible" title="历史文档" width="40%">
      <el-table :data="fileList" v-loading="listLoading" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button size="small" @click="loadExistingDocument(scope.row.name)">加载</el-button>
            <el-button size="small" type="danger" @click="removeDocument(scope.row.name)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="listDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showImageDialog"
      title="选择图片"
      width="50%"
      class="image-select-dialog"
    >
      <el-table :data="imageFiles" height="400">
        <el-table-column prop="name" label="图片名称" width="180">
          <template #default="{row}">
            <span>{{ getFileIcon(row.name) }}</span>
            {{ row.name }}
          </template>
        </el-table-column>
        <el-table-column label="预览" width="120">
          <template #default="{row}">
            <img 
              :src="`http://localhost:5000/documents/${row.name}`" 
              style="max-width: 100px; max-height: 60px; object-fit: contain;"
              alt="预览"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button
              size="small"
              @click="insertExistingImage(`http://localhost:5000/documents/${row.name}`)"
            >
              插入
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VMdEditor from '@kangc/v-md-editor'
import '@kangc/v-md-editor/lib/style/base-editor.css'
import githubTheme from '@kangc/v-md-editor/lib/theme/github.js'
import '@kangc/v-md-editor/lib/theme/style/github.css'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

VMdEditor.use(githubTheme)

export default defineComponent({
  name: 'MarkdownEditor',
  setup() {
    const markdownText = ref('')
    const currentFilename = ref('')
    const fileList = ref([])
    const listDialogVisible = ref(false)
    const listLoading = ref(false)
    const searchQuery = ref('')
    const compiledMarkdown = computed(() => {
      return VMdEditor.vMdParser.themeConfig.markdownParser.render(markdownText.value)
    })
    const pdfPreviewUrl = ref('')
    const fileInputRef = ref(null)
    const imageInputRef = ref(null)
    const pdfDialogVisible = ref(false)
    const showImageDialog = ref(false)
    const imageFiles = ref([])
    const editorWidth = ref(50)
    const isDragging = ref(false)
    const imageWidthPercent = ref(70)
    const previewZoom = ref(100)
    const sidebarCollapsed = ref(false)
    const previewRef = ref(null)
    const showImgHandle = ref(false)
    const imgHandleLeft = ref(0)
    const imgHandleTop = ref(0)
    let selectedImg = null
    let imgStartWidth = 0
    let imgResizeStartX = 0
    const filteredFiles = computed(() => {
      const q = (searchQuery.value || '').toLowerCase()
      if (!q) return fileList.value
      return fileList.value.filter(i => i.name.toLowerCase().includes(q))
    })

    const insertText = (prefix, suffix) => {
      const start = prefix || ''
      const end = suffix || ''
      markdownText.value = `${markdownText.value}${start}${end}`
    }

    const getFileIcon = (filename) => {
      const ext = filename.split('.').pop().toLowerCase()
      switch(ext) {
        case 'md': return '📝'
        case 'pdf': return '📄'
        case 'jpg': case 'jpeg': case 'png': case 'gif': return '🖼️'
        case 'txt': return '📄'
        default: return '📁'
      }
    }

    const normalizeFilename = (name) => {
      if (!name) return ''
      return name
    }

    const saveDocument = async () => {
      try {
        const { data } = await axios.post('http://localhost:5000/api/save-document', {
          content: markdownText.value,
          filename: normalizeFilename(currentFilename.value) || undefined
        })
        if (data && data.status === 'success') {
          ElMessage.success('保存成功：' + (data.filename || '未命名.md'))
          currentFilename.value = data.filename || currentFilename.value
          fetchFileList()
        } else {
          ElMessage.error('文档保存失败')
        }
      } catch (error) {
        ElMessage.error('文档保存失败')
      }
    }

    const fetchFileList = async () => {
      try {
        listLoading.value = true
        const { data } = await axios.get('http://localhost:5000/api/list-documents')
        fileList.value = (data?.files || []).map(name => ({ name }))
      } catch (error) {
        ElMessage.error('获取文档列表失败')
      } finally {
        listLoading.value = false
      }
    }

    const importDocument = async () => {
      try {
        listLoading.value = true
        const { data } = await axios.get('http://localhost:5000/api/list-documents')
        fileList.value = (data?.files || []).map(name => ({ name }))
        listDialogVisible.value = true
      } catch (error) {
        ElMessage.error('获取文档列表失败')
      } finally {
        listLoading.value = false
      }
    }

    const exportDocument = () => {
      const blob = new Blob([markdownText.value || ''], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `document-${Date.now()}.md`
      a.click()
      URL.revokeObjectURL(url)
    }

    const openPdfDialog = () => {
      pdfDialogVisible.value = true
    }

    const toggleExpand = () => {
      editorWidth.value = editorWidth.value < 40 ? 50 : 30
    }

    const startDrag = (e) => {
      isDragging.value = true
      const startX = e.clientX
      const startWidth = editorWidth.value
      const onMove = (ev) => {
        if (!isDragging.value) return
        const dx = ev.clientX - startX
        const total = document.querySelector('.editor-container').clientWidth
        const deltaPercent = (dx / total) * 100
        let next = startWidth + deltaPercent
        next = Math.max(15, Math.min(85, next))
        editorWidth.value = next
      }
      const onUp = () => {
        isDragging.value = false
        window.removeEventListener('mousemove', onMove)
        window.removeEventListener('mouseup', onUp)
      }
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    }

    const triggerImport = () => {
      pdfPreviewUrl.value = ''
      if (fileInputRef.value) fileInputRef.value.click()
    }

    const handleFileChange = async (e) => {
      const file = e.target.files && e.target.files[0]
      e.target.value = ''
      if (!file) return
      
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        const { data } = await axios.post('http://localhost:5000/api/upload-document', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (data.status === 'success') {
          ElMessage.success('文件上传成功')
          fetchFileList()
          
          // 自动打开上传的文件
          if (file.type.startsWith('image/')) {
            markdownText.value = `![](${data.fileUrl})`
          } else if (file.name.endsWith('.pdf')) {
            pdfPreviewUrl.value = data.fileUrl
          } else if (file.name.endsWith('.md') || file.name.endsWith('.txt')) {
            const { data: contentData } = await axios.get('http://localhost:5000/api/load-document', {
              params: { filename: file.name }
            })
            markdownText.value = contentData.content || ''
          }
          
          currentFilename.value = file.name
        } else {
          ElMessage.error('文件上传失败')
        }
      } catch (error) {
        ElMessage.error('文件上传失败')
      }
    }

    const triggerInsertImage = () => {
      if (imageInputRef.value) imageInputRef.value.click()
    }

    const openImageDialog = async () => {
      try {
        await fetchFileList()
        showImageDialog.value = true
        
        // 过滤出图片文件
        imageFiles.value = fileList.value.filter(file => {
          const ext = file.name.split('.').pop().toLowerCase()
          return ['jpg', 'jpeg', 'png', 'gif'].includes(ext)
        })
      } catch (e) {
        ElMessage.error('加载图片列表失败')
      }
    }

    const handleImageChange = (e) => {
      const file = e.target.files && e.target.files[0]
      e.target.value = ''
      if (!file) return
      const url = URL.createObjectURL(file)
      markdownText.value = `${markdownText.value}\n![](${url})\n`
      ElMessage.success('已插入图片')
    }

    const insertExistingImage = (imageUrl) => {
      markdownText.value = `${markdownText.value}\n![](${imageUrl})\n`
      showImageDialog.value = false
      ElMessage.success('已插入图片')
    }

    const updateHandlePosition = () => {
      if (!selectedImg || !previewRef.value) return
      const imgRect = selectedImg.getBoundingClientRect()
      const contRect = previewRef.value.getBoundingClientRect()
      imgHandleLeft.value = imgRect.right - contRect.left - 8 + previewRef.value.scrollLeft
      imgHandleTop.value = imgRect.bottom - contRect.top - 8 + previewRef.value.scrollTop
      showImgHandle.value = true
    }

    const onPreviewClick = (e) => {
      const t = e.target
      if (t && t.tagName === 'IMG') {
        selectedImg = t
        updateHandlePosition()
      } else {
        selectedImg = null
        showImgHandle.value = false
      }
    }

    const startImageResize = (e) => {
      if (!selectedImg) return
      imgResizeStartX = e.clientX
      imgStartWidth = selectedImg.getBoundingClientRect().width
      const onMove = (ev) => {
        const dx = ev.clientX - imgResizeStartX
        const next = Math.max(40, imgStartWidth + dx)
        selectedImg.style.width = next + 'px'
        selectedImg.style.maxWidth = 'none'
        updateHandlePosition()
      }
      const onUp = () => {
        window.removeEventListener('mousemove', onMove)
        window.removeEventListener('mouseup', onUp)
      }
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    }

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      if (sidebarCollapsed.value && editorWidth.value < 40) editorWidth.value = 50
    }

    const toggleEditorExpand = () => {
      editorWidth.value = editorWidth.value > 60 ? 40 : 70
    }

    const loadExistingDocument = async (filename) => {
      try {
        const ext = filename.split('.').pop().toLowerCase()
        
        if (ext === 'pdf') {
          const url = `http://localhost:5000/documents/${filename}`
          pdfPreviewUrl.value = url
          currentFilename.value = filename
          markdownText.value = ''
          ElMessage.success('已加载PDF文件：' + filename)
          return
        }
        
        if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
          const url = `http://localhost:5000/documents/${filename}`
          markdownText.value = `![](${url})`
          currentFilename.value = filename
          pdfPreviewUrl.value = ''
          ElMessage.success('已加载图片：' + filename)
          return
        }

        const { data } = await axios.get('http://localhost:5000/api/load-document', { params: { filename } })
        if (data && data.status === 'success') {
          markdownText.value = data.content || ''
          currentFilename.value = filename
          pdfPreviewUrl.value = ''
          listDialogVisible.value = false
          ElMessage.success('已加载文档：' + filename)
        } else {
          ElMessage.error('加载失败')
        }
      } catch (e) {
        ElMessage.error('加载失败')
      }
    }

    const removeDocument = async (filename) => {
      try {
        await ElMessageBox.confirm(`确认删除文件 "${filename}" 吗？`, '删除确认', {
          confirmButtonText: '删除',
          cancelButtonText: '取消',
          type: 'warning'
        })
      } catch (e) {
        return
      }
      try {
        await axios.delete('http://localhost:5000/api/delete-document', { params: { filename } })
        ElMessage.success('已删除：' + filename)
        fetchFileList()
        if (currentFilename.value === filename) {
          currentFilename.value = ''
          markdownText.value = ''
        }
      } catch (e) {
        ElMessage.error('删除失败')
      }
    }

    const renameDocument = async (oldName) => {
      try {
        const { value: newName } = await ElMessageBox.prompt('请输入新文件名', '重命名', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValue: oldName,
          inputPattern: /.+/,
          inputErrorMessage: '请输入有效文件名'
        })
        
        if (newName === oldName) return
        
        const { data } = await axios.post('http://localhost:5000/api/rename-document', {
          oldName,
          newName
        })
        
        if (data?.status === 'success') {
          ElMessage.success(`已重命名: ${oldName} → ${newName}`)
          fetchFileList()
          if (currentFilename.value === oldName) {
            currentFilename.value = newName
          }
        } else {
          ElMessage.error('重命名失败')
        }
      } catch (e) {
        if (e !== 'cancel') {
          ElMessage.error('重命名失败')
        }
      }
    }

    const newDocument = () => {
      markdownText.value = ''
      currentFilename.value = ''
      ElMessage.success('已新建空白文档')
    }

    const scrollPreview = (direction) => {
      const previewEl = previewRef.value
      if (!previewEl) return
      const scrollStep = previewEl.clientHeight * 0.5
      const scrollAmount = direction === 'up' ? -scrollStep : scrollStep
      previewEl.scrollBy({
        top: scrollAmount,
        behavior: 'smooth'
      })
    }

    onMounted(() => {
      fetchFileList()
      if (previewRef.value) {
        previewRef.value.addEventListener('click', onPreviewClick)
        previewRef.value.addEventListener('scroll', updateHandlePosition)
        previewRef.value.scrollTo(0, 0)
      }
    })

    onBeforeUnmount(() => {
      isDragging.value = false
      if (previewRef.value) {
        previewRef.value.removeEventListener('click', onPreviewClick)
        previewRef.value.removeEventListener('scroll', updateHandlePosition)
      }
    })

    return {
      markdownText,
      compiledMarkdown,
      insertText,
      saveDocument,
      importDocument,
      exportDocument,
      fileList,
      listDialogVisible,
      listLoading,
      loadExistingDocument,
      fetchFileList,
      currentFilename,
      searchQuery,
      filteredFiles,
      newDocument,
      removeDocument,
      triggerImport,
      handleFileChange,
      triggerInsertImage,
      handleImageChange,
      fileInputRef,
      imageInputRef,
      pdfPreviewUrl,
      pdfDialogVisible,
      editorWidth,
      startDrag,
      toggleExpand,
      toggleEditorExpand,
      imageWidthPercent,
      previewZoom,
      openPdfDialog,
      sidebarCollapsed,
      toggleSidebar,
      previewRef,
      showImgHandle,
      imgHandleLeft,
      imgHandleTop,
      startImageResize,
      renameDocument,
      scrollPreview,
      getFileIcon,
      openImageDialog,
      insertExistingImage,
      showImageDialog,
      imageFiles
    }
  }
})
</script>

<style scoped>
.markdown-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.toolbar {
  margin-bottom: 10px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.editor-container {
  display: flex;
  flex: 1;
  gap: 20px;
}

.sidebar {
  width: 260px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  background: var(--el-bg-color);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-toggle {
  position: absolute;
  right: -10px;
  top: 8px;
  width: 16px;
  height: 16px;
  border-radius: 8px;
  background: var(--el-color-primary);
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.sidebar-header {
  padding: 10px;
  border-bottom: 1px solid var(--el-border-color);
}

.sidebar-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.sidebar-list {
  padding: 6px 0;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.file-item {
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.file-icon {
  margin-right: 8px;
}

.file-item:hover {
  background: var(--el-fill-color-light);
}

.file-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.editor-pane, .preview-pane {
  height: 100%;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  background: var(--el-bg-color);
  display: flex;
  flex-direction: column;
}

.editor-pane :deep(.el-textarea) {
  flex: 1;
  display: flex;
}

.editor-pane :deep(.el-textarea__inner) {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px;
  height: 100% !important;
}

.pane-header, .preview-header {
  padding: 8px 10px;
  border-bottom: 1px solid var(--el-border-color);
}

.divider {
  width: 6px;
  cursor: col-resize;
  background: var(--el-border-color);
  border-radius: 3px;
}

.preview-tools {
  display: flex;
  gap: 12px;
  align-items: center;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  transform: scale(var(--preview-zoom, 1));
  transform-origin: 0 0;
}

.preview-content::-webkit-scrollbar {
  width: 8px;
}

.preview-content::-webkit-scrollbar-track {
  background: var(--el-bg-color);
}

.preview-content::-webkit-scrollbar-thumb {
  background-color: var(--el-color-primary-light-5);
  border-radius: 4px;
}

.preview-content {
  scrollbar-width: thin;
  scrollbar-color: var(--el-color-primary-light-5) var(--el-bg-color);
}

.preview-content :deep(img) {
  width: var(--img-max-width, 70%);
  max-width: 100%;
  height: auto;
  image-rendering: auto;
  display: block;
}

.pdf-frame {
  width: 100%;
  height: 70vh;
  border: 0;
}

.img-resize-handle {
  position: absolute;
  width: 14px;
  height: 14px;
  background: var(--el-color-primary);
  border-radius: 7px;
  cursor: nwse-resize;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.preview-pane {
  position: relative;
}

.image-select-dialog .el-dialog__body {
  padding: 20px;
}
</style>