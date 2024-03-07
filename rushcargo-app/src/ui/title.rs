use ratatui::{
    layout::{Layout, Direction, Constraint},
    prelude::{Alignment, Frame, Modifier},
    style::{Color, Style},
    text::{Line, Span, Text},
    symbols::Marker,
    widgets::{
        canvas::{
            Canvas,
            Points
        },
        List,
        Block,
        BorderType,
        Borders,
        Paragraph,
    }
};
use std::sync::{Arc, Mutex};
use crate::{
    HELP_TEXT,
    model::{
        common::{Popup, Screen, InputMode, TimeoutType},
        app::App,
    },
    ui::common_fn::{
        centered_rect,
        percent_x,
        percent_y,
        clear_chunks,
    }
};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) {
    let mut app_lock = app.lock().unwrap();

    /*let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(8),
            Constraint::Length(2),
            Constraint::Length(8),
        ])
        .split(centered_rect(
            percent_x(f, 1.5),
            percent_y(f, 1.8),
            f.size()));

    let lower_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(10),
            Constraint::Percentage(35),
            Constraint::Percentage(5),
            Constraint::Percentage(55),
        ])
        .split(chunks[2]);

    let actions_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(1),
            Constraint::Length(3),
            Constraint::Percentage(100),
        ])
        .split(lower_chunks[1]);

    let title_block = Block::default().borders(Borders::ALL).border_type(BorderType::QuadrantOutside);

    let title = Paragraph::new(Text::from(
        app_lock.title.as_ref().unwrap().text.clone()
    ))
    .block(title_block)
    .alignment(Alignment::Center);

    f.render_widget(title, chunks[0]);

    let actions = List::new(
        app_lock.list.actions.title.clone()
    ).highlight_style(Style::default().add_modifier(Modifier::REVERSED));

    f.render_stateful_widget(actions, actions_chunks[1], &mut app_lock.list.state.0);*/

    //let width = lower_chunks[3].width as f64;
    //let height = lower_chunks[3].height as f64;
    let width = f.size().width as f64;
    let height = f.size().height as f64;

    let canvas = Canvas::default()
        .marker(Marker::Dot)
        .paint(|ctx| {
            for dot in app_lock.title.as_ref().unwrap().cube.rot_dot.iter() {
                let xp = dot.x * 1.0 / (12.0 - dot.z);
                let yp = dot.y * 1.0 / (12.0 - dot.z);
                //ctx.print(xp, yp, "*");
                ctx.print(dot.x * 10.0, dot.y * 10.0, "*");
            }
            ctx.print(0.0, -0.0, "0");
        })
        .x_bounds([-(width / 2.0), width / 2.0])
        .y_bounds([-(height / 2.0), height / 2.0])
        .block(Block::default().borders(Borders::ALL));

    f.render_widget(canvas, f.size());
}