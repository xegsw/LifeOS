#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod deepseek;
mod runtime;
mod secure_credentials;

fn main() {
    runtime::run();
}
