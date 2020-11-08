<template>
    <div>
        <vs-navbar center-collapsed v-model="active" color="primary" text-white>
            <template #right>
                <div v-if="own_route !== null">
                    <vs-button color="dark" @click="copyUrl()">
                        <i class='bx bxs-copy' ></i> Get Local Onion Route
                    </vs-button>
                </div>
            </template>
        </vs-navbar>
    </div>
</template>


<script>
export default {
    name:"NavBar",
    data:() => ({
        active:'guide'
    }),
    props:{
        own_route: String
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
        }

    }
}
</script>

<style>

</style>