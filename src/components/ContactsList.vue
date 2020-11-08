<template>
    <div class="grid">
        <vs-row justify="center">
            <vs-button @click="new_contact_dialog=!new_contact_dialog">
                Add Contact
            </vs-button>
        </vs-row>
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

        <p v-for="contact in contacts" :key="contact.address">
            {{contact.name}}
        </p>
    </div>
</template>

<script>
export default {
    name:"ContactsList",
    data:() => ({
        new_contact_dialog:false,
        contacts:[],
        new_contact:{
            address:'',
            name:''
        }
    }),
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
        }
    }
}
</script>

<style>

</style>