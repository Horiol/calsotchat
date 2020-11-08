<template>
    <vs-alert shadow :color="color" flat style="margin:10px">
        <template #title>
            <div v-bind:class="{ my_message_title: isMine }">
                <span v-if="isMine">You</span>
                <span v-else>{{contact.name}}</span>
            </div>
        </template>
            <div v-bind:class="{ my_message: isMine }">
                {{message.msg}}
            </div>
    </vs-alert>
</template>

<script>
export default {
    name: 'Message',
    props:{
        message:Object,
        contact:Object
    },
    computed:{
        isMine(){
            if ('destiny' in this.message){
                return true
            } else {
                return false
            }
        },
        color: function(){
            if ('destiny' in this.message){
                return 'primary'
            } else {
                return "dark"
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