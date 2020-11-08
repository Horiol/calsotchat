<template>
  <div>
    <p>
      Destiny address:
      <input type="text" v-model="destiny">
    </p>
    <p>
      Message:
      <input type="text" v-model="msg">
    </p>
    <button @click="sendMessage()">Send</button>
    <br>
    <br>
    Messages received:
    <br>
    <p v-for="message in messages" :key="message.timestamp">
      <strong>{{message.origin}}</strong> -> {{message.msg}}
    </p>
  </div>
</template>

<script>
export default {
  name: 'Chat',
  data:() => ({
    msg:'',
    destiny:'',
    messages:[],
  }),
  methods: {
    sendMessage(){
      console.log("Sending message to " + this.destiny);
      var msg_data = {
        destiny: this.destiny,
        msg: this.msg
      }
      this.$socket.emit('send-message', msg_data)
    }
  },
  sockets: {
    newMessage: function (data) {
        this.messages.push(data)
    }
  },

}
</script>

<style>

</style>