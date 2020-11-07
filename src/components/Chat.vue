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
  </div>
</template>

<script>
export default {
  name: 'Chat',
  data:() => ({
    msg:'',
    destiny:''
  }),
  methods: {
    sendMessage(){
      console.log("Sending message to " + this.destiny);
      this.axios
      .post('http://127.0.0.1:5000/api/send_message', {
        destiny: this.destiny,
        msg: this.msg
      })
      .then(response => (console.log(response)))
    }
  }
}
</script>

<style>

</style>