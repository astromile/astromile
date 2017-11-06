<template>
	<div class="entry">
		<div class="entry-label" v-bind:style="{width:wlabel}">{{label}}</div>
		<div class="entry-value">
			<input type="text"
				:id="id"
				v-model="currentValue"
				@keypress.enter="onChange"
				@blur="onChange"
				@keyup.esc="currentValue=value"
				:disabled="disabled"
				:size="wvalue" />

		</div>
	</div>
</template>

<script>

module.exports = {
	name: 'Entry',
	props: ['id','label','value','wlabel','wvalue','disabled'],
	data: function(){
		return {
			currentValue:this.value
		}
	},
	methods: {
		onChange: function(e){
			if(this.value != this.currentValue){
				this.$emit('input', this.currentValue, this.id)
			}
		}
	},
	watch: {
		value: function(){
			this.currentValue=this.value
		}
	}
}

</script>

<style>
	.entry-label {
		float: left;
	}
	.entry-value {
		float:left;
	}
</style>