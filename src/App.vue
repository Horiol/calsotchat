<template>
  <div id="app">
    <h3>
      {{own_route}}
    </h3>
    <Chat />
  </div>
</template>

<script>
import Chat from './components/Chat.vue'

export default {
  name: 'App',
  components: {
    Chat
  },
  data:() => ({
    own_route:null
  }),
  mounted: function(){
    if (this.own_route === null){
      this.$socket.emit('update-status')
    }
  },
  sockets: {
    statusResponse: function(data) {
      this.own_route = data.own_route
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
