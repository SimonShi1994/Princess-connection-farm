<template>
  <div id="app">
    <div>
      <span>这是导航栏</span>
      <a href="/">首页</a>
      <a href="/task">任务</a>
      <a href="/config">配置</a>
    </div>

    <hr/>

    <router-view/>
  </div>
</template>

<script>

export default {
  name: 'app'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
