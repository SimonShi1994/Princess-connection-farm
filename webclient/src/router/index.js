import Vue from 'vue'
import Router from 'vue-router'
import TaskConfig from '@/pages/TaskConfig'
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
      path: '/task_config',
      name: 'TaskConfig',
      component: TaskConfig
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
