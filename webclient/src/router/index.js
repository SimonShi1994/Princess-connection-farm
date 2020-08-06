import Vue from 'vue'
import Router from 'vue-router'
import Task from '@/pages/Task'
import Dashboard from '@/pages/Dashboard'
import AccountConfig from '@/pages/AccountConfig'
import ClanConfig from '@/pages/ClanConfig'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/account_config'
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: Dashboard
    },
    {
      path: '/task',
      name: 'Task',
      component: Task
    },
    {
      path: '/account_config',
      name: 'AccountConfig',
      component: AccountConfig
    },
    {
      path: '/clan_config',
      name: 'ClanConfig',
      component: ClanConfig
    }
  ]
})
