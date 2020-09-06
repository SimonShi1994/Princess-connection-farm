<template>
  <div id="app" style="height: 100%">
    <el-container direction="vertical" style="height: 100%">

      <el-header style="border-bottom: solid 1px #e6e6e6; height: 61px">
        <el-row type="flex">
          <el-col :span="2" :offset="1">
            <el-avatar :size="59" shape="square" fit="fit" src="/static/favicon.ico"></el-avatar>
          </el-col>
          <el-col :span="5">
            <p style="text-align: left;margin-top: 20px">Princess Connection Farm</p>
          </el-col>

          <el-col :span="15">
            <Menu/>
          </el-col>
        </el-row>
      </el-header>
      <el-main style="padding: 0;background-color: #f6f8fa;">

      <el-row>
        <el-col :span="16" :offset="4">
            <el-container>
              <el-main>
                <router-view/>
              </el-main>
            </el-container>
        </el-col>
      </el-row>
      </el-main>

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

html {
  height: 100%;
}

body {
  height: 100%;
  margin: 0;
}

</style>
