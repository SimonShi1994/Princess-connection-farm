import Vue from 'vue'
import Router from 'vue-router'
import Index from '@/components/Index'
import Config from '@/components/Config'
import Task from '@/components/Task'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Index',
      component: Index
    },
    {
      path: '/task',
      name: 'Task',
      component: Task
    },
    {
      path: '/config',
      name: 'Config',
      component: Config
    }
  ]
})
