<template>
    <vs-col w="6">
        <vs-alert shadow :color="color" flat style="margin:10px">
            <template #title>
                <div v-bind:class="{ my_message_title: isMine }">
                    <span v-if="isMine">You</span>
                    <span v-else>{{message.sender.name}}</span>
                </div>
            </template>
                <div v-bind:class="{ my_message: isMine }">
                    {{message.msg}}
                </div>
        </vs-alert>
    </vs-col>
</template>

<script>
export default {
    name: 'Message',
    props:{
        message:Object,
        myself: Object
    },
    computed:{
        isMine(){
            if (this.message.sender.address == this.myself.address){
                return true
            } else {
                return false
            }
        },
        color: function(){
            if (this.message.sender.address == this.myself.address){
                return "success"
            } else {
                return 'primary'
            }
        }
    }
}
</script>

<style>
.my_message{
    text-align: end;
}
.my_message_title{
    text-align: end;
    display: block;
    width: 100%;
}
</style>