<template>
    <div class="hidden">
        <vs-sidebar open v-model="active" absolute>
            <vs-sidebar-item v-for="user in contacts" :key="user.name" :id="user.name">
                {{user.name}}
            </vs-sidebar-item>
        </vs-sidebar>
    </div>
</template>


<script>
export default {
    name: 'Sidebar',
    data:() => ({
        active:null,
        contacts:[
            {name:'oriol'},
            {name:'oscar'},
            {name:'sendo'},
            {name:'test'},
        ]
    }),
    mounted() {
        this.active = this.contacts[0].name
    },
    watch: {
        active: function(new_user) {
            //do something when the data changes.
            if (new_user) {
                console.log("User selected: " + new_user);
            }
        }
    }

}
</script>
