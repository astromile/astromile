<template>
	<div class="dropdown">
		<div class="dropdown-label"
		     v-bind:style="{width:wlabel}">{{label}}</div>
		<div class="dropodown-value">
			<select :id="id"
			        :value="value"
			        @change="onChange"
			        :disabled="disabled">
				<option v-for="(item,i) in items"
				        :key="item">{{item}}</option>
			</select>
		</div>
	</div>
</template>

<script>

module.exports = {
	name: 'Dropdown',
	props: ['id', 'label', 'value', 'items', 'wlabel', 'wvalue', 'disabled'],
	data: function() {
		return {
			currentValue: this.value
		}
	},
	methods: {
		onChange: function(e) {
			if (this.value != e.target.value) {
				this.$emit('input', e.target.value, this.id)
			}
		}
	},
	watch: {
		value: function() {
			this.currentValue = this.value
		}
	}
}

</script>

<style>
.dropdown-label {
	float: left;
}

.dropdown-value {
	float: left;
}
</style>