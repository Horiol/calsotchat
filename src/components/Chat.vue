<template>
  <div class="grid">
    <vs-row justify="center" v-if="contact === null">
      <h3>Select a contact to start a chat</h3>
    </vs-row>
    <div class="hidden" v-else>
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
          v-for="message in messages" 
          :key="message.timestamp"
        >
          <message :message="message"/>
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
    contact:Object
  },
  data:() => ({
    active:false,
    msg:'',
    destiny:'',
    messages:[
      {
        timestamp:1,
        origin: "gxf3xsmy6trcaugd5pvfpr652qxnzizx4zxf5smcwtczobters37awad.onion:8080",
        name: "Test User",
        msg: "test message"
      }
    ],
  }),
  methods: {
    author(message){
      if ('destiny' in message){
        return 'You'
      } else {
        return message.origin
      }
    },
    sendMessage(){
      if (this.msg !== ''){
        var msg_data = {
          destiny: this.destiny,
          msg: this.msg,
          timestamp: Date.now()
        }
        this.$socket.emit('send-message', msg_data)
        this.messages.push(msg_data)
        this.msg = ''
        this.active = false
      }
    },
    check_message_origin: function(message){
      if ('destiny' in message){
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
    contact: function(){
      if (this.contact !== null){
        this.destiny = this.contact.address
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
  max-height: calc(75vh - 50px);
}
</style>