use objc2::{rc::Retained, AnyThread, MainThreadMarker};
use objc2_app_kit::{NSApplication, NSImage, NSWorkspace, NSWorkspaceIconCreationOptions};
use objc2_foundation::{NSBundle, NSData};

fn image_from_bytes(bytes: &[u8]) -> Option<Retained<NSImage>> {
    NSImage::initWithData(NSImage::alloc(), &NSData::with_bytes(bytes))
}

pub fn set_dock_icon(bytes: &[u8]) {
    let Some(mtm) = MainThreadMarker::new() else {
        return;
    };
    let Some(image) = image_from_bytes(bytes) else {
        return;
    };
    let app = NSApplication::sharedApplication(mtm);
    // AppKit receives a valid, retained image and is called on the main thread.
    unsafe { app.setApplicationIconImage(Some(&image)) };
}

pub fn set_bundle_icon(bytes: Option<&[u8]>) {
    let image = match bytes {
        Some(bytes) => match image_from_bytes(bytes) {
            Some(image) => Some(image),
            None => return,
        },
        None => None,
    };
    let bundle_path = NSBundle::mainBundle().bundlePath();
    let _ = NSWorkspace::sharedWorkspace().setIcon_forFile_options(
        image.as_deref(),
        &bundle_path,
        NSWorkspaceIconCreationOptions::empty(),
    );
}
