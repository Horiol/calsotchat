<template>
    <div>
        <vs-navbar center-collapsed v-model="active" color="primary" text-white>
            <template #right>
                <div v-if="ca_api_token !== null">
                    <vs-button success @click="active_dialog=true">
                        <i class='bx bx-search'></i> Search contact
                    </vs-button>
                </div>
                <div v-else>
                    <vs-button color="warn" @click="active_dialog_login=true">
                        <i class='bx bx-plus'></i> Signup in CA
                    </vs-button>
                </div>
                <div v-if="own_route !== null">
                    <vs-button color="dark" @click="copyUrl()">
                        <i class='bx bxs-copy' ></i> Get Local Onion Route
                    </vs-button>
                </div>
            </template>
        </vs-navbar>

        <vs-dialog v-model="active_dialog">
            <template #header>
                <h4 class="not-margin">
                    Search Contact
                </h4>
            </template>
            <div class="con-content">
                <vs-input v-model="contact_email" label-placeholder="Email">
                    <template #icon>
                        @
                    </template>
                </vs-input>
            </div>
            <template #footer>
                <div class="con-footer">
                    <vs-button @click="SearchCA">
                        Search
                    </vs-button>
                </div>
            </template>
        </vs-dialog>

        <vs-dialog v-model="active_dialog_login">
            <template #header>
                <h4 class="not-margin">
                    Signup in CA
                </h4>
            </template>
            <div class="con-content">
                <vs-input v-model="contact_email" label-placeholder="Your email">
                    <template #icon>
                        @
                    </template>
                </vs-input>
            </div>
            <template #footer>
                <div class="con-footer">
                    <vs-button @click="postToCA">
                        Sign Up
                    </vs-button>
                </div>
            </template>
        </vs-dialog>
    </div>
</template>


<script>
export default {
    name:"NavBar",
    data:() => ({
        active:'guide',
        active_dialog:false,
        active_dialog_login:false,
        contact_email: ''
    }),
    props:{
        own_route: String,
        ca_api_token: String,
    },
    methods:{
        copyUrl() {
            const el = document.createElement('textarea');
            el.value = this.own_route;
            el.setAttribute('readonly', '');
            el.style.position = 'absolute';
            el.style.left = '-9999px';
            document.body.appendChild(el);
            const selected =  document.getSelection().rangeCount > 0  ? document.getSelection().getRangeAt(0) : false;
            el.select();
            document.execCommand('copy');                   
            document.body.removeChild(el);
            if (selected) {
                document.getSelection().removeAllRanges();
                document.getSelection().addRange(selected);   
            }

            this.$vs.notification({
                icon:`<i class='bx bx-select-multiple' ></i>`,
                title: 'Route copied',
                text: `Local onion route copied successfully into the clipboard`
            })
        },
        SearchCA() {
            this.axios
            .post('/find_contact/', {
                "email": this.contact_email,
                "api_token": this.ca_api_token
            })
            .then((_response) => {
                this.active_dialog = false
            })
            .catch(error => {
                console.log(error);
                if (error.response.status == 409){
                    this.$vs.notification({
                        icon:`<i class='bx bx-error' ></i>`,
                        title: 'Conflict Error',
                        text: `Contact address already in contacts list`
                    })
                }
                else if (error.response.status == 404){
                    this.$vs.notification({
                        icon:`<i class='bx bx-error' ></i>`,
                        title: 'Not Found',
                        text: `Email not found in CalsotChat-CA`
                    })
                }
                else if (error.response.status == 403){
                    this.$vs.notification({
                        icon:`<i class='bx bx-error' ></i>`,
                        title: 'Forbidden',
                        text: `Please confirm your email before search for contacts`
                    })
                }
            })
        },
        postToCA() {
            this.axios
            .put('/myself/', {
                "email": this.contact_email
            })
            .then((response) => {
                this.$emit('new-api-token', response.data.api_token)
                this.active_dialog_login = false
                this.$vs.notification({
                    icon:`<i class='bx bx-mail-send'></i>`,
                    title: 'Confirm email',
                    text: `Check your inbox to confirm the email`
                })
            })
        }
    },
    watch: {
        active_dialog_login: function(){
            this.contact_email = ''
        },
        active_dialog: function(){
            this.contact_email = ''
        }
    }
}
</script>

<style>

</style>