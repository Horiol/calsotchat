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
            <vs-sidebar-item v-if="contacts.length == 0" id="no_contacts">
                
            </vs-sidebar-item>

            <vs-sidebar-item v-for="contact in contacts" :id="contact.hash" :key="contact.hash">
                <template #icon>
                    <span v-if="contact.members.length == 1">
                        <vs-avatar badge :badge-color="userStatus(contact.members[0])" badge-position="top-right">
                            <i class='bx bx-user'></i>
                        </vs-avatar>
                    </span>
                    <span v-else>
                        <vs-avatar>
                            <i class='bx bx-group'></i>
                        </vs-avatar>
                    </span>
                </template>
                {{contact.name}}
                <span v-if="contact.hash == myself.address">
                    (You)
                </span>
                <vs-button v-if="has_new_messages(contact.hash)" circle success transparent :active="true" icon style="display:inline">
                    <i class='bx bxs-message-detail' ></i>
                </vs-button>
            </vs-sidebar-item>

            <template #footer>
                <vs-button @click="new_contact_dialog=true">
                    <i class='bx bxs-user-plus' ></i> Add Contact
                </vs-button>
                <vs-button @click="new_group_dialog=true">
                    <i class='bx bxs-group' ></i> New group
                </vs-button>
            </template>
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

        <vs-dialog v-model="new_group_dialog" :loading="loading_dialog">
            <template #header>
                <h4 class="not-margin">
                    New Group
                </h4>
            </template>
            <div class="con-form">
                <vs-input v-model="new_group.name" label-placeholder="Group name">
                    <template #icon>
                        <i class='bx bxs-group' ></i>
                    </template>
                </vs-input>
                <br>
                <vs-select
                    label="Members"
                    multiple
                    v-model="new_group.members"
                >
                    <vs-option v-for="contact in private_contacts" :label="contactName(contact)" :value="contact" :key="contact.id">
                        {{contactName(contact)}}
                    </vs-option>
                </vs-select>
            </div>
            <template #footer>
                <div class="footer-dialog">
                    <vs-button block @click="addNewGroup()">
                        Create group
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
        new_messages_rooms: [],
        active:null,
        loading_dialog: false,
        new_contact:{
            address:'',
            name:''
        },
        new_group_dialog: false,
        new_group: {
            name: '',
            members: []
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
        },
        new_group_dialog: function(){
            this.new_group = {
                name:'',
                members:[]
            }
        }
    },
    computed:{
        private_contacts: function(){
            var th = this;
            var private_rooms = this.contacts.filter(function(contact){
                if (contact.hash == th.myself.address){
                    return false
                }
                return contact.private
            })

            return private_rooms.map(room => room.members[0])
        },
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
        has_new_messages: function(room_hash) {
            return this.new_messages_rooms.indexOf(room_hash) >= 0
        },
        contactName: function(contact){
            if (contact.name != null){
                return contact.name
            }else{
                return contact.nickname
            }
        },
        userStatus: function(contact){
            if (contact.online){
                return "success"
            } else {
                return "danger"
            }
        },
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
                    .then(_response => {
                        // this.$emit('new-contact', response.data)
                        this.loading_dialog = false
                        this.new_contact_dialog = false 
                    })
                })
            }
        },
        addNewGroup:function(){
            // this.new_group.members.push(this.myself)

            this.loading_dialog = true
            this.axios
            .post('/rooms/', this.new_group)
            .then(response => {
                console.log(response)
                // this.$emit('new-contact', response.data)
                this.loading_dialog = false
                this.new_group_dialog = false
            })
        },
        userSelected: function(room_hash){
            var room = this.contacts.filter(function(element){
                return element.hash == room_hash
            })[0]
            this.$emit('input', room)

            if (this.new_messages_rooms.indexOf(room_hash) >= 0){
                this.new_messages_rooms.splice(this.new_messages_rooms.indexOf(room_hash), 1)
            }
        }
    },
    sockets: {
        newMessage: function (data) {
            if (this.active !== data.room_hash){
                this.new_messages_rooms.push(data.room_hash)
            }
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
.vs-select-content{
    max-width: none !important;
}
.vs-select__chips__chip__close{
    display: none !important;
}
</style>