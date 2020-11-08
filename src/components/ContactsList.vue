<template>
    <div class="hidden">
        <vs-sidebar 
        absolute 
        v-model="active" 
        v-on:input="userSelected" 
        open>
            <template #header>
                <h3>Contacts</h3>
            </template>
            <template #footer>
                <vs-button @click="new_contact_dialog=!new_contact_dialog">
                    <i class='bx bxs-user-plus' ></i> Add Contact
                </vs-button>
            </template>

            <vs-sidebar-item v-for="contact in contacts" :id="contact.address" :key="contact.address">
                {{contact.name}}
            </vs-sidebar-item>
        </vs-sidebar>

        <vs-dialog v-model="new_contact_dialog">
            <template #header>
                <h4 class="not-margin">
                    New Contact
                </h4>
            </template>


            <div class="con-form">
                <vs-input v-model="new_contact.address" label-placeholder="Onion Address">
                    <template #icon>
                        @
                    </template>
                    <template v-if="!validAddress" #message-danger>
                        Address not valid
                    </template>
                </vs-input>
                <vs-input v-model="new_contact.name" label-placeholder="Name">
                    <template #icon>
                        <i class='bx bxs-user' ></i>
                    </template>
                </vs-input>
            </div>

            <template #footer>
                <div class="footer-dialog">
                    <vs-button block @click="addNewContact()">
                        Add contact
                    </vs-button>
                </div>
            </template>
        </vs-dialog>
    </div>
</template>

<script>
export default {
    name:"ContactsList",
    data:() => ({
        new_contact_dialog:false,
        contacts:[
            {
                address:'gxf3xsmy6trcaugd5pvfpr652qxnzizx4zxf5smcwtczobters37awad.onion:8080',
                name:'Test User'
            },
            {
                address:'another address',
                name:'Another User'
            }
        ],
        active:null,
        new_contact:{
            address:'',
            name:''
        }
    }),
    mounted: function(){
        if (this.contacts.length > 0){
            this.active = this.contacts[0].address
            this.$emit('input', this.contacts[0])
        }
    },
    watch: {
        new_contact_dialog: function(){
            this.new_contact = {
                address:'',
                name:''
            }
        }
    },
    computed:{
        validAddress: function(){
            if (this.new_contact.address.length == 0){
                return true
            }

            var th = this
            var already_added = this.contacts.filter(function(element){
                return element.address == th.new_contact.address
            }).length

            if (already_added>0){
                return false
            }else{
                return true
            }
        }
    },
    methods:{
        addNewContact: function(){
            if (this.validAddress){
                this.contacts.push(this.new_contact)
                this.new_contact_dialog = false 
            }
        },
        userSelected: function(user_address){
            var contact = this.contacts.filter(function(element){
                return element.address == user_address
            })[0]
            this.$emit('input', contact)
        }
    },
    sockets: {
        contactList: function(data) {
            this.contacts = data
        }
    }
}
</script>

<style>

</style>