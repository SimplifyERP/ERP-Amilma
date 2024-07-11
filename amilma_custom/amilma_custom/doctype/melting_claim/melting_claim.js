// Copyright (c) 2023, Vivek and contributors
// For license information, please see license.txt

frappe.ui.form.on('Melting Claim', {
	onload:function(frm){
		get_total_qty(frm)
		calculateTotalAmount(frm)
	}

});

frappe.ui.form.on('Melting Claim Items', {
	item: function (frm, cdt, cdn) {
		if (frm.doc.outlet) {
			var doc = locals[cdt][cdn]
			frappe.call({
				method: "amilma_custom.amilma_custom.doctype.melting_claim.melting_claim.get_item_rate",
				args: {
					item: doc.item
				},
				callback(r) {
					doc.rate = r.message
					doc.req_qty = 1
					doc.amount = doc.rate * doc.req_qty
					frm.refresh_field("melting_claim_items")

					get_total_qty(frm)

					var total_amount = 0;
					$.each(frm.doc.melting_claim_items, function (i, d) {
						total_amount += d.amount;
						frm.set_value("net_total", total_amount);
					});
				}
			})
			calculateTotalAmount(frm)
		}
	},
	req_qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.req_qty * row.rate;
		frm.refresh_field("melting_claim_items")
		calculateTotalAmount(frm)
		get_total_qty(frm)
	},
	before_melting_claim_items_remove: function (frm, cdt, cdn) {
		var deleted_row = frappe.get_doc(cdt, cdn);
		var total_qty = frm.doc.total_qty - deleted_row.req_qty
		frm.set_value("total_qty", total_qty);

		var deleted_row = frappe.get_doc(cdt, cdn);
		var net_total = frm.doc.net_total - deleted_row.amount
		frm.set_value("net_total", net_total);
	}
});
function calculateTotalAmount(frm) {
	var total_amount = 0;
	$.each(frm.doc.melting_claim_items, function (i, d) {
		total_amount += d.amount;
	});
	frm.set_value("net_total", total_amount);
	frm.refresh_field('melting_claim_items');
}
function get_total_qty(frm) {
	var total_qty = 0;
	$.each(frm.doc.melting_claim_items, function (i, d) {
		total_qty += d.req_qty;
	});
	frm.set_value("total_qty", total_qty);
	frm.refresh_field('melting_claim_items');
}
