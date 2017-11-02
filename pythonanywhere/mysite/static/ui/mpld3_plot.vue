<template>
    <div :id="id" 
    	:class="{plotting: plotting, placeholder: data==null}"
    	>
    </div>
</template>

<script>
//import d3 from '../3rd-party/d3.js'
//import mpld3 from '../3rd-party/mpld3.js'

module.exports = {
    name: 'MplD3Plot',
    props: {
        id: { type: String, required: true },
        data: { type: Object },
        plotting: {type: Boolean}
    },
    mounted() {
        this.plot()
    },
    watch: {
        data: function (value) {
            this.plot()
        }
    },
    methods: {
        plot: function () {
            if (this.data != null && Object.keys(this.data).length > 0) {
                d3.select('#' + this.id).selectAll('*').remove()
                mpld3.draw_figure(this.id, this.data)
            }
        }
    }
}
</script>

<style>
	.plotting{
		background-color: #ffa;
	}
	.placeholder{
		width: 640px;
		height: 484px;
	}
</style>