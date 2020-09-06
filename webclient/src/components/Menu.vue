<template>
  <div>
    <el-row class="tac">
      <el-col :span="24">
        <el-menu :default-active="this.$route.path"
                 router
                 mode="horizontal">
          <el-menu-item v-for="(item,i) in navList"
                        :key="i"
                        :index="item.name">
            <template slot="title">
              <span> {{ item.navItem }}</span>
            </template>
          </el-menu-item>
        </el-menu>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'Menu',
  data () {
    return {
      navList: [
        {name: '/dashboard', navItem: '总览'},
        {name: '/task_config', navItem: '任务'},
        {name: '/account_config', navItem: '账号'},
        {name: '/clan_config', navItem: '行会'}
      ]
    }
  }
}
</script>

<style scoped>

</style>
