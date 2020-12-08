<template>
  <div class="grid">
    <vs-row justify="center" v-if="room === null">
      <h3>Select a contact to start a chat</h3>
    </vs-row>
    <div class="hidden" v-else>
      <vs-row>
        <h2>
          <span v-if="room.hash == myself.address">
            (You)
          </span>
          {{room.name}}
          <vs-button 
            v-if="canEdit"
            style="display:inline"
            icon
            @click="openModal"
          >
            <i class='bx bxs-pencil' ></i>
          </vs-button>
        </h2>
      </vs-row>
      <vs-row justify="center" align="center">
        <vs-col w="11">
          <div class="con-form">
            <vs-input
              @keyup.enter="sendMessage()"
              primary
              v-model="msg"
              placeholder="Write a new message" 
            />
          </div>
        </vs-col>
        <vs-col w="1">
          <vs-button 
            icon
            @click="sendMessage()"
          >
            <i class='bx bxs-paper-plane' ></i>
          </vs-button>
        </vs-col>
      </vs-row>
      <div id="chat-window">
        <vs-row 
          :justify="check_message_origin(message)"
          v-for="message in messages" 
          :key="message.id"
        >
          <message :message="message" :myself="myself"/>
        </vs-row>
      </div>
    </div>

    <vs-dialog v-model="active" :loading="loading_dialog">
      <template #header>
          <h4 class="not-margin">
            New Name
          </h4>
      </template>
      <div class="con-form">
        <vs-input v-model="new_name" label-placeholder="Name" @keyup.enter="saveName">
            <template #icon>
              <i class='bx bxs-user' ></i>
            </template>
        </vs-input>
        <br>
        <vs-select
            v-if="!room.private"
            label="Members"
            multiple
            v-model="new_members"
        >
            <vs-option v-for="contact in private_contacts" :label="contactName(contact)" :value="contact.id" :key="contact.id">
                {{contactName(contact)}}
            </vs-option>
        </vs-select>
      </div>
      <template #footer>
          <div class="footer-dialog">
              <vs-button block @click="saveName">
                  Save Name
              </vs-button>
          </div>
      </template>
    </vs-dialog>
  </div>
</template>

<script>
import Message from './Message.vue'
export default {
  name: 'Chat',
  components:{
    Message
  },
  props:{
    room:Object,
    myself:Object,
    contacts: Array
  },
  data:() => ({
    active:false,
    new_name:'',
    new_members: [],
    msg:'',
    messages:[],
    loading_dialog: false
  }),
  mounted: function(){
    if (this.room !== null){
      this.loadMessages()
    }
  },
  methods: {
    contactName: function(contact){
        if (contact.name != null){
            return contact.name
        }else{
            return contact.nickname
        }
    },
    loadMessages(){
      this.new_name = this.room.name
      this.axios
        .get('/rooms/' + this.room.hash + "/messages/")
        .then((response) => {
          this.messages = response.data.reverse()
        })
    },
    sendMessage(){
      if (this.msg !== ''){
        var msg_data = {
          room_hash: this.room.hash,
          msg: this.msg
        }
        this.$socket.emit('send-message', msg_data) // TODO: add message to the conversation automatically?

        msg_data['sender'] = this.myself
        this.msg = ''
      }
    },
    check_message_origin: function(message){
      if (message.sender.address == this.myself.address){
        return 'flex-end'
      } else {
        return 'flex-start'
      }
    },
    openModal: function(){
      this.active = true
    },
    saveName: function(){
      this.loading_dialog = true
      if (!this.room.private){
        const old_ids = this.room.members.map(member => member.id)
        var ids_2_add = []
        var ids_2_delete = []
  
        for (let index = 0; index < this.new_members.length; index++) {
          const new_member_id = this.new_members[index];
          if (!old_ids.includes(new_member_id)){
            ids_2_add.push(new_member_id)
          }
        }
        if(ids_2_add.length>0){
          this.axios
          .post('/rooms/' + this.room.hash + '/members/', {
              "members": ids_2_add
          })
        }
  
        for (let index = 0; index < old_ids.length; index++) {
          const old_id = old_ids[index];
          if (!this.new_members.includes(old_id)){
            ids_2_delete.push(old_id)
          }
        }
        if(ids_2_delete.length>0){
          this.axios
          .delete('/rooms/' + this.room.hash + '/members/', {
            data:{
              "members": ids_2_delete
            }
          })
        }
      }

      this.axios
      .put('/rooms/' + this.room.hash + '/', {
          "name": this.new_name
      })
      .then(response => {
        this.$emit('update-room', response.data)
        this.loading_dialog = false
        this.active = false
      })
    }
  },
  sockets: {
    newMessage: function (data) {
      if (this.room !== null){
        // var address_array = this.room.members.map(member => member.address);
        // if (address_array.indexOf(data.sender_address) > -1){ // TODO: Improve this function when adding groups feature
        //   this.messages.push(data)
        // }
        if (data.room_hash == this.room.hash){
          this.messages.push(data)
        }
      }
    },
    updateMessage: function(data) {
      for (let index = 0; index < this.messages.length; index++) {
        const message = this.messages[index]
        if (message.id == data.id){
          this.$set(this.messages, index, data)
        }        
      }
    }
  },
  watch:{
    room: function(){
      if (this.room !== null){
        this.new_members = this.room.members.map(member => member.id)
        this.loadMessages()
      }
    },
    messages: function(){
      var th = this
      setTimeout(function(){
        var container = th.$el.querySelector("#chat-window");
        container.scrollTop = container.scrollHeight;
      }, 100) // wait 100ms because the message is displayed in the UI properlly before scroll
    }
  },
  computed:{
    canEdit: function(){
      if (this.room.private){
        return true
      }else{
        return (this.room.admin_address == this.myself.address)
      }
    },  
    private_contacts: function(){
        var th = this;
        var private_rooms = this.contacts.filter(function(contact){
            if (contact.hash == th.myself.address){
                return false
            }
            return contact.private
        })
        console.log(private_rooms);
        return private_rooms.map(room => room.members[0])
    }
  }
}
</script>

<style>
#chat-window{
  margin-right:50px;
  margin-left:50px;
  overflow-y: auto;
  overflow-x:hidden;
  max-height: calc(75vh - 50px);
}
</style>