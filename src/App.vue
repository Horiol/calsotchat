<template>
  <div id="app">
    <nav-bar :own_route="myself.address" :ca_api_token="ca_api_token" @new-api-token="updateToken"/>
    <contacts-list 
      :myself="myself"
      v-on:input="userSelected" 
      :contacts="contacts"
      @new-contact="addContact"
    />
    <div class="grid main-window">
      <vs-row>
        <vs-col w="12">
          <chat 
            :myself="myself" 
            :room="selected_contact"
            :contacts="contacts"
            @update-room="updateRoom"
            @remove-contact="removeContact"
          />
        </vs-col>
      </vs-row>
    </div>

    <vs-dialog not-close prevent-close v-model="notHaveNickname">
            <template #header>
                <h4 class="not-margin">
                  Write your Nickname
                </h4>
            </template>


        <div class="con-form">
            <vs-input v-model="new_nickname" label-placeholder="Nickname" @keyup.enter="saveNickname">
                <template #icon>
                  <i class='bx bxs-user' ></i>
                </template>
                <template v-if="!validNickname" #message-danger>
                  Nickname not valid
                </template>
            </vs-input>
        </div>

        <template #footer>
            <div class="footer-dialog">
                <vs-button block @click="saveNickname">
                    Set Nickname
                </vs-button>
            </div>
        </template>
    </vs-dialog>
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
    notHaveNickname: false,
    validNickname: true,
    myself:{
      address:null,
      nickname:null
    },
    ca_api_token: null,
    new_nickname:"",
    selected_contact:null,
    contacts: [],
    loading: null
  }),
  mounted: function(){
    this.loading = this.$vs.loading()
    this.mainLoad()
  },
  methods:{
    updateToken: function(token) {
      this.ca_api_token = token
    },
    removeContact: function(data) {
      this.contacts = this.contacts.filter(contact => contact.hash != data.hash)

      if (this.selected_contact.hash == data.hash) {
        this.selected_contact = this.contacts[0]
      }
    },
    updateRoom: function(data){
      for (let index = 0; index < this.contacts.length; index++) {
        const room = this.contacts[index];
        if (room.id == data.id){
          this.$set(this.contacts, index, data)
          if (this.selected_contact.id == data.id){
            this.selected_contact = data
          }
        }
      }
    },
    mainLoad: function(){
      this.axios.all([
        this.axios
          .get('/myself/'),
        this.axios
          .get('/rooms/')
      ])
      .then(this.axios.spread((first_response, second_response) => {
        this.myself = first_response.data['contact']
        this.ca_api_token = first_response.data['api_token']
        this.notHaveNickname = (this.myself.nickname == "")

        this.contacts = second_response.data
        this.loading.close()
      }))
      .catch(error => {
        console.log(error);
        var th = this
        setTimeout(
          function() {th.mainLoad()},
          1000
        )
      })
    },
    addContact: function(room){
      this.contacts.push(room)
    },
    userSelected: function(room){
      this.selected_contact = room
    },
    saveNickname: function(){
      if (this.new_nickname != ""){
        this.axios
          .put('/contacts/'+this.myself.address+'/', {
            "name": this.new_nickname,
            "nickname": this.new_nickname,
            "address": this.myself.address
          })
          .then((_response) => {
            this.loading = this.$vs.loading()
            this.mainLoad()
          })
        }else{
          this.validNickname = false
        }
      }
  },
  sockets: {
    newContact: function (data) {
      this.contacts.push(data)
    },
    contactUpdate: function(data) {
      for (let index = 0; index < this.contacts.length; index++) {
        const room = this.contacts[index];
        if (room.hash == data.address){
          this.contacts[index]['members'] = [data]
        }
      }
      // TODO: what to do in groups?
    }
  }
}
</script>

<style>

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin-top: 60px;
  overflow-x: hidden;
  color: rgba(var(--vs-primary), 1);
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
