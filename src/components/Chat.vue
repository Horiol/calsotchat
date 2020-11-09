<template>
  <div class="grid">
    <vs-row justify="center" v-if="room === null">
      <h3>Select a contact to start a chat</h3>
    </vs-row>
    <div class="hidden" v-else>
      <vs-row><h2>{{room.name}}</h2></vs-row>
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
          :key="message.timestamp"
        >
          <message :message="message" :myself="myself"/>
        </vs-row>
      </div>
    </div>
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
  },
  data:() => ({
    active:false,
    msg:'',
    messages:[
      // {
      //   timestamp:1,
      //   origin: "gxf3xsmy6trcaugd5pvfpr652qxnzizx4zxf5smcwtczobters37awad.onion:8080",
      //   name: "Test User",
      //   msg: "test message"
      // }
    ],
  }),
  methods: {
    sendMessage(){
      if (this.msg !== ''){
        var msg_data = {
          room_hash: this.room.hash,
          msg: this.msg
        }
        this.$socket.emit('send-message', msg_data)

        msg_data['sender'] = this.myself
        this.messages.push(msg_data)
        this.msg = ''
        this.active = false
      }
    },
    check_message_origin: function(message){
      if (message.sender.id == this.myself.id){
        return 'flex-end'
      } else {
        return 'flex-start'
      }
    }
  },
  sockets: {
    newMessage: function (data) {
        this.messages.push(data)
    }
  },
  watch:{
    room: function(){
      if (this.room !== null){
        this.axios
          .get('http://localhost:5000/api/rooms/' + this.room.hash + "/messages/")
          .then((response) => {
            this.messages = response.data.reverse()
          })
      }
    },
    messages: function(){
      var th = this
      setTimeout(function(){
        var container = th.$el.querySelector("#chat-window");
        container.scrollTop = container.scrollHeight;
      }, 100) // wait 100ms because the message is displayed in the UI properlly before scroll
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