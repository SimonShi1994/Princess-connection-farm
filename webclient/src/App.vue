<template>
  <div id="app">
    <el-container>

      <el-header style="border-bottom: solid 1px #e6e6e6;height: 61px">
        <el-container>
          <el-aside>
            <p >Princess Connection Farm</p>
          </el-aside>
          <el-main style="padding: 0">
            <Menu/>
          </el-main>
        </el-container>
      </el-header>

      <el-main style="padding: 0;margin: 0 15% 0 15%;">
        <el-container>
          <el-main>
            <router-view/>
          </el-main>
        </el-container>
      </el-main>

      <el-footer>

      </el-footer>

    </el-container>
  </div>
</template>

<script>
import Menu from '@/components/Menu'

export default {
  name: 'app',
  components: {Menu}
}
</script>

<style>

</style>
