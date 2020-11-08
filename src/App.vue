<template>
  <div id="app">
    <nav-bar :own_route="own_route"/>
    <contacts-list v-on:input="userSelected"/>
    <div class="grid main-window">
      <vs-row>
        <vs-col w="12">
          <chat :contact="selected_contact"/>
        </vs-col>
      </vs-row>
    </div>
  </div>
</template>

<script>
import Chat from './components/Chat.vue'
import ContactsList from './components/ContactsList.vue'
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: {
    Chat,
    ContactsList,
    NavBar
  },
  data:() => ({
    own_route:null,
    selected_contact:null
  }),
  mounted: function(){
    if (this.own_route === null){
      this.$socket.emit('update-status')
    }
  },
  methods:{
    userSelected: function(user){
      this.selected_contact = user
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
  color: #2c3e50;
  margin-top: 60px;
  overflow-x: hidden;
}

.main-window{
  margin-left: 280px;
}

.not-margin {
  margin: 0px;
  font-weight: normal;
  padding: 10px;
}
.con-form {
  width: 100%;
}
.con-form .flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.con-form .flex a {
  font-size: 0.8rem;
  opacity: 0.7;
}
.con-form .flex a:hover {
  opacity: 1;
}
.con-form .vs-checkbox-label {
  font-size: 0.8rem;
}
.con-form .vs-input-content {
  margin: 10px 0px;
  width: calc(100%);
}
.con-form .vs-input-content .vs-input {
  width: 100%;
}
.footer-dialog {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: calc(100%);
}
.footer-dialog .new {
  margin: 0px;
  margin-top: 20px;
  padding: 0px;
  font-size: 0.7rem;
}
.footer-dialog .new a {
  color: getColor('primary') !important;
  margin-left: 6px;
}
.footer-dialog .new a:hover {
  text-decoration: underline;
}
.footer-dialog .vs-button {
  margin: 0px;
}

</style>
