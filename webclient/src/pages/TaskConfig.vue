<template>
  <div>
    <el-card>
      <el-row type="flex" class="row-bg" justify="end">
        <el-col :span="2">
          <el-button
            size="mini"
            type="success"
            @click="dialogCreateFormVisible = true">新增
          </el-button>
        </el-col>
      </el-row>

      <el-dialog title="添加任务" :visible.sync="dialogCreateFormVisible"
                 @close="()=>{dialogCreateFormVisible = false;createForm = {taskname: ''}}">
        <el-form :model="createForm">
          <el-form-item label="任务名">
            <el-input v-model="createForm.taskname" autocomplete="off"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="()=>{dialogCreateFormVisible = false;createForm = {taskname: ''}}">取 消</el-button>
          <el-button type="primary" @click="handleCreate(createForm.taskname)">确 定</el-button>
        </div>
      </el-dialog>

      <el-dialog title="编辑任务" :visible.sync="dialogUpdateFormVisible" width="80%"
                 @close="handleCancelEdit()">
        <el-form :model="updateForm">
          <el-form-item label="任务名">
            <el-input disabled v-model="updateForm.row.taskname" autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="关联账号">
            <el-input disabled v-model="updateForm.row.accounts" autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="子任务列表">
            <el-table
              :data="updateForm.row.subtasks.tasks"
              stripe
              style="width: 100%">
              <el-table-column
                prop="type"
                label="ID"
                width="50"
              >
              </el-table-column>

              <el-table-column
                label="名称" width="80">
                <template slot-scope="scope">
                  {{subtaskSchema[scope.row.type].title}}
                </template>
              </el-table-column>

              <el-table-column
                label="描述" width="100">
                <template slot-scope="scope">
                  {{subtaskSchema[scope.row.type].desc}}
                </template>
              </el-table-column>

              <el-table-column
                label="参数">
                <template slot-scope="scope">
                  <el-table
                    v-if="subtaskSchema[scope.row.type].params.length>0"
                    :data="subtaskSchema[scope.row.type].params"
                    stripe
                    style="width: 100%">
                    <el-table-column
                      prop="key"
                      label="变量"
                      width="100">
                    </el-table-column>
                    <el-table-column
                      prop="key_type"
                      label="类型"
                      width="50">
                    </el-table-column>
                    <el-table-column
                      prop="title"
                      label="名称"
                      width="80">
                    </el-table-column>
                    <el-table-column
                      prop="desc"
                      label="描述"
                      width="300">
                    </el-table-column>
                    <el-table-column
                      label="值">
                      <template slot-scope="scope1">
                        <el-input v-if='scope1.row.key_type !== "bool"' v-model='scope.row[scope1.row.key]'></el-input>
                        <el-switch
                          v-if='scope1.row.key_type === "bool"'
                          v-model='scope.row[scope1.row.key]'
                          active-text="True"
                          inactive-text="False">
                        </el-switch>
                      </template>
                    </el-table-column>
                  </el-table>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="50">
                <template slot-scope="scope">
                  <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="deleteSubtask(scope.$index)"></el-button>
                </template>
              </el-table-column>

            </el-table>
          </el-form-item>
          <el-form-item label="添加子任务">
            <el-select v-model="updateForm.row.newSubtask" placeholder="请选择">
              <el-option
                v-for="item in subtaskSchema"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                :disabled="item.disabled">
              </el-option>
            </el-select>
            <el-button type="success" icon="el-icon-check" circle @click="addSubtask()"></el-button>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="handleCancelEdit()">取 消</el-button>
          <el-button type="primary" @click="handleSubmitEdit()">确 定</el-button>
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
            <el-button
              size="mini"
              @click="handleStartEdit(scope.$index, scope.row)">编辑
            </el-button>
            <el-popconfirm
              title="确定删除这个任务吗？"
              @onConfirm="handleDelete(scope.$index, scope.row)">
              <el-button
                slot="reference"
                size="mini"
                type="danger"
                @click="preHandleDelete(scope.$index, scope.row)">删除
              </el-button>
            </el-popconfirm>
          </template>

        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>

import {listTask, createTask, deleteTask, listSubtaskSchema, updateTask} from '@/request/api'

export default {
  name: 'TaskConfig',
  data () {
    return {
      tableData: [],
      search: '',

      dialogCreateFormVisible: false,
      createForm: {
        taskname: ''
      },

      dialogUpdateFormVisible: false,
      updateForm: {
        index: null,
        row: {
          taskname: '',
          accounts: '',
          subtasks: {tasks: []},
          newSubtask: ''
        }
      },

      subtaskSchema: {}
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
        this.dialogCreateFormVisible = false
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
      this.updateForm.index = index
      this.updateForm.row = row
      console.log(this.updateForm.row)

      this.dialogUpdateFormVisible = true
    },
    addSubtask () {
      let abbr = this.updateForm.row.newSubtask
      let templateSubtask = {
        'type': abbr
      }
      let params = this.subtaskSchema[abbr].params
      for (let i = 0; i < params.length; i++) {
        templateSubtask[params[i].key] = null
      }
      this.updateForm.row.subtasks.tasks.push(templateSubtask)
      this.updateForm.row.newSubtask = ''
      console.log(templateSubtask)
    },
    deleteSubtask (index) {
      console.log(this.updateForm.row.subtasks.tasks)
      this.updateForm.row.subtasks.tasks.splice(index, 1)
    },
    handleSubmitEdit () {
      console.log(this.updateForm.row)
      updateTask(this.updateForm.row.taskname, this.updateForm.row.subtasks).then(res => {
        this.$notify({
          title: '更新成功',
          message: this.updateForm.row.taskname,
          type: 'success'
        })
        this.dialogUpdateFormVisible = false
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
    handleCancelEdit () {
      console.log(this.updateForm.row)

      this.dialogUpdateFormVisible = false
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
      listTask().then(res => {
        console.log(res)
        this.tableData = res.data
      }).catch(err => {
        this.tableData = [{
          taskname: 'mana号任务',
          accounts: '张三,罗某'
        }, {
          taskname: '装备号任务',
          accounts: '某翔,韩立'
        }, {
          taskname: '大号任务',
          accounts: '咕噜灵波'
        }
        ]
        this.$notify({
          title: '后端未启动, 加载演示数据',
          message: err,
          type: 'success'
        })
      })

      listSubtaskSchema().then(res => {
        let data = res.data
        for (let i = 0; i < data.length; i++) {
          this.subtaskSchema[data[i].abbr] = data[i]
          this.subtaskSchema[data[i].abbr].value = data[i].abbr
          this.subtaskSchema[data[i].abbr].label = data[i].abbr + '(' + data[i].title + ')'
        }
        console.log(res)
        console.log('load schema')
        console.log(this.subtaskSchema)
      })
    }
  }
}
</script>

<style scoped>

</style>
