<template>
  <div>
    <el-card>
      <el-row type="flex" class="row-bg" justify="end">
        <el-col :span="2">
          <el-button
            size="mini"
            type="success"
            @click="dialogFormVisible = true">新增
          </el-button>
        </el-col>
      </el-row>

      <el-dialog title="添加账户" :visible.sync="dialogFormVisible"
                 @close="()=>{dialogFormVisible = false;form = {taskname: ''}}">
        <el-form :model="form">
          <el-form-item label="任务名">
            <el-input v-model="form.taskname" autocomplete="off"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="()=>{dialogFormVisible = false;form = {taskname: ''}}">取 消</el-button>
          <el-button type="primary" @click="handleCreate(form.taskname)">确 定</el-button>
        </div>
      </el-dialog>

      <el-table
        :data="tableData.filter(data => !search || data.taskname.toLowerCase().includes(search.toLowerCase()) || data.accounts.toLowerCase().includes(search.toLowerCase()))"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange">
        >
        <el-table-column
          type="selection"
          width="55">
        </el-table-column>
        <el-table-column
          label="任务"
          prop="taskname">
        </el-table-column>
        <el-table-column
          label="关联账号 (开发中)"
          prop="accounts">
        </el-table-column>
        <el-table-column
          align="right">
          <template slot="header" slot-scope="scope">
            <el-input
              v-model="search"
              size="mini"
              placeholder="任务/关联账号"/>
          </template>

          <template slot-scope="scope">
<!--            <el-button-->
<!--              v-if="!scope.row.edit"-->
<!--              size="mini"-->
<!--              @click="handleStartEdit(scope.$index, scope.row)">编辑-->
<!--            </el-button>-->
            <el-popconfirm
              v-if="!scope.row.edit"
              title="确定删除这个任务吗？"
              @onConfirm="handleDelete(scope.$index, scope.row)">
              <el-button
                v-if="!scope.row.edit"
                slot="reference"
                size="mini"
                type="danger"
                @click="preHandleDelete(scope.$index, scope.row)">删除
              </el-button>
            </el-popconfirm>
            <el-button
              v-if="scope.row.edit"
              size="mini"
              type="success"
              @click="handleSubmitEdit(scope.$index, scope.row)">确定
            </el-button>
            <el-button
              v-if="scope.row.edit"
              size="mini"
              @click="handleCancelEdit(scope.$index, scope.row)">取消
            </el-button>
          </template>

        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import {listTask, createTask, updateTask, deleteTask} from '@/request/api'

export default {
  name: 'TaskConfig',
  data () {
    return {
      tableData: [],
      search: '',
      dialogFormVisible: false,
      form: {
        taskname: ''
      }
    }
  },
  mounted () {
    this.refreshTableData()
  },
  methods: {
    handleCreate (taskname) {
      createTask(taskname).then(res => {
        this.$notify({
          title: '创建成功',
          message: taskname,
          type: 'success'
        })
        this.dialogFormVisible = false
        this.refreshTableData()
      }).catch(err => {
        if (err.response && err.response.status) {
          this.$notify({
            title: err.response.data.msg,
            message: '',
            type: 'error'
          })
        } else {
          this.$notify({
            title: err,
            message: '',
            type: 'error'
          })
        }
      })
    },
    handleStartEdit (index, row) {
      row.edit = !row.edit
    },
    handleCancelEdit (index, row) {
      row.edit = !row.edit
    },
    handleSubmitEdit (index, row) {
      row.edit = !row.edit

      updateTask(row.taskname).then(res => {
        this.$notify({
          title: '修改成功',
          message: row.taskname,
          type: 'success'
        })
        this.refreshTableData()
      }).catch(err => {
        if (err.response && err.response.status) {
          this.$notify({
            title: err.response.data.msg,
            message: '',
            type: 'error'
          })
        } else {
          this.$notify({
            title: err,
            message: '',
            type: 'error'
          })
        }
      })
    },
    handleDelete (index, row) {
      deleteTask(row.taskname).then(res => {
        this.$notify({
          title: '删除成功',
          message: row.taskname,
          type: 'success'
        })
        this.refreshTableData()
      }).catch(err => {
        if (err.response && err.response.status) {
          this.$notify({
            title: err.response.data.msg,
            message: '',
            type: 'error'
          })
        } else {
          this.$notify({
            title: err,
            message: '',
            type: 'error'
          })
        }
      })
    },
    preHandleDelete (index, row) {
    },
    handleSelectionChange (val) {
      this.multipleSelection = val
    },
    refreshTableData () {
      var _this = this
      listTask().then(res => {
        console.log(res)
        for (var i = 0; i < res.data.length; i++) {
          res.data[i]['edit'] = false
        }
        _this.tableData = res.data
      }).catch(err => {
        _this.tableData = [{
          taskname: 'mana号任务',
          accounts: '张三,罗某',
          edit: false
        }, {
          taskname: '装备号任务',
          accounts: '某翔,韩立',
          edit: false
        }, {
          taskname: '大号任务',
          accounts: '咕噜灵波',
          edit: false
        }
        ]
        this.$notify({
          title: '后端未启动, 加载演示数据',
          message: err,
          type: 'success'
        })
      })
    }
  }
}
</script>

<style scoped>

</style>
