<template>
    <div class="hidden">
        <vs-sidebar 
        absolute 
        v-model="active" 
        v-on:input="userSelected" 
        open>
            <template #logo>
                <img class="custom-logo" src="@/assets/icon.png">
            </template>
            <template #header>
                <h3>Contacts</h3>
            </template>
            <template #footer>
                <vs-button @click="new_contact_dialog=!new_contact_dialog">
                    <i class='bx bxs-user-plus' ></i> Add Contact
                </vs-button>
            </template>
            <vs-sidebar-item v-if="contacts.length == 0" id="no_contacts">
                
            </vs-sidebar-item>

            <vs-sidebar-item v-for="contact in contacts" :id="contact.hash" :key="contact.hash">
                <span v-if="contact.hash == myself.address">
                    (You)
                </span>
                {{contact.name}}
            </vs-sidebar-item>
        </vs-sidebar>

        <vs-dialog v-model="new_contact_dialog" :loading="loading_dialog">
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
    props:{
        contacts:Array,
        myself: Object,
    },
    data:() => ({
        new_contact_dialog:false,
        active:null,
        loading_dialog: false,
        new_contact:{
            address:'',
            name:''
        }
    }),
    mounted: function(){
        // if (this.contacts.length > 0){
        //     this.active = this.contacts[0].address
        //     this.$emit('input', this.contacts[0])
        // }
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
                this.loading_dialog = true
                this.axios
                .post('/contacts/', {
                    "name": this.new_contact.name,
                    "nickname": this.new_contact.name,
                    "address": this.new_contact.address
                })
                .then(response => {
                    this.axios
                    .get('/rooms/' + response.data.address + "/")
                    .then(response => {
                        this.$emit('new-contact', response.data)
                        this.loading_dialog = false
                        this.new_contact_dialog = false 
                    })
                })
            }
        },
        userSelected: function(room_hash){
            var room = this.contacts.filter(function(element){
                return element.hash == room_hash
            })[0]
            this.$emit('input', room)
        }
    }
}
</script>

<style>
/* .vs-sidebar-content .vs-sidebar__logo img{ */
.custom-logo{
    max-width: 120px !important;
    max-height: 120px !important;
}
</style>