function setupEmailComposerDefaults() {
	frappe.provide("frappe.views");
	const v = frappe.views;
	const existing = v.CommunicationComposer;

	function wrap(Cls) {
		return class extends Cls {
			prepare() {
				// Force "Attach Document Print" unchecked by default
				this.attach_document_print = false;
				super.prepare();
			}
		};
	}

	let wrapped = null;
	Object.defineProperty(v, "CommunicationComposer", {
		get: () => wrapped != null ? wrapped : v._CommunicationComposerOriginal,
		set: (Cls) => {
			v._CommunicationComposerOriginal = Cls;
			wrapped = Cls && Cls.name !== "CommunicationComposerNoAttachPrint" ? wrap(Cls) : Cls;
		},
		configurable: true,
		enumerable: true,
	});

	if (existing && typeof existing === "function") {
		wrapped = wrap(existing);
		v._CommunicationComposerOriginal = existing;
	}
}
setupEmailComposerDefaults();