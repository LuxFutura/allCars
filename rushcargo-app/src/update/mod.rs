mod common;
mod list;
mod table;
mod login;
mod client;

use std::sync::{Arc, Mutex};
use sqlx::PgPool;
use anyhow::Result;
use crate::{
    event::Event,
    model::app::App,
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::Quit | Event::TimeoutTick(_) | Event::KeyInput(..) |
        Event::SwitchInput | Event::SwitchAction | Event::SelectAction |
        Event::EnterScreen(_) | Event::EnterPopup(_) | Event::TryGetUserLocker(_, _)
        => common::update(app, pool, event).await,

        Event::NextListItem(_) | Event::PrevListItem(_) | Event::SelectListItem(_)
        => list::update(app, pool, event).await,

        Event::NextTableItem(_) | Event::PrevTableItem(_) | Event::SelectTableItem(_)
        => table::update(app, pool, event).await,

        Event::TryLogin
        => login::update(app, pool, event).await,

        Event::Resize
        => Ok(()),

        _ => panic!("received event {:?} without assigned function", event)
    }
}