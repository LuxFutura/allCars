use std::time::{Duration, Instant};
use tui_input::Input;
use rust_decimal::Decimal;
use super::{
    client::ClientData,
    pkgadmin::PkgAdminData,
    db_obj::{Package, ShippingGuide, Locker, Payment},
};

#[derive(Debug, Clone)]
pub enum Screen {
    Title,
    Settings,
    Login,
    Client(SubScreen),
    PkgAdmin(SubScreen),
}

#[derive(Debug, Clone)]
pub enum SubScreen {
    ClientMain,
    ClientLockers,
    ClientLockerPackages,
    ClientSentPackages,

    PkgAdminMain,
    PkgAdminGuides,
    PkgAdminGuideInfo,
    PkgAdminAddPackage(Div),
}

#[derive(Debug, Clone)]
pub enum Div {
    Left,
    Right
}

impl std::fmt::Display for Screen {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}",
            match self {
                Screen::Title => "Title",
                Screen::Settings => "Settings",
                Screen::Login => "Login",
                Screen::Client(_) => "Client",
                Screen::PkgAdmin(_) => "Package Admin",
            }
        )
    }
}

#[derive(Debug, Clone)]
pub enum Popup {
    Prev,
    OrderSuccessful,
    DisplayMsg,

    LoginSuccessful,

    ClientOrderMain,
    ClientOrderLocker,
    ClientOrderBranch,
    ClientOrderDelivery,
    ClientInputPayment,

    FieldExcess,
}

#[derive(Debug)]
pub enum User {
    Client(ClientData),
    PkgAdmin(PkgAdminData),
}

pub enum InputMode {
    Normal,
    /// The value represents the InputField being edited
    Editing(u8),
}

pub struct InputFields(pub Input, pub Input);

#[derive(Eq, PartialEq, Hash, Debug, Clone, Copy)]
pub enum TimeoutType {
    Resize,
    CubeTick,
    Login,
    GetUserDelivery,
}

pub struct Timer {
    pub counter: u8,
    pub tick_rate: Duration,
    pub last_update: Instant,
}

#[derive(Debug)]
pub struct PackageData {
    pub viewing_packages: Vec<Package>,
    pub viewing_packages_idx: i64,
    pub selected_packages: Option<Vec<Package>>,
    pub active_package: Option<Package>,
}

impl std::default::Default for PackageData {
    fn default() -> Self {
        PackageData {
            viewing_packages: Vec::new(),
            viewing_packages_idx: 0,
            selected_packages: None,
            active_package: None,
        }
    }
}

#[derive(Debug)]
pub struct ShippingGuideData {
    pub viewing_guides: Vec<ShippingGuide>,
    pub viewing_guides_idx: i64,
    pub active_guide: Option<ShippingGuide>,
    pub active_guide_payment: Option<Payment>,
}

impl std::default::Default for ShippingGuideData {
    fn default() -> Self {
        ShippingGuideData {
            viewing_guides: Vec::new(),
            viewing_guides_idx: 0,
            active_guide: None,
            active_guide_payment: None,
        }
    }
}

#[derive(Debug)]
pub enum Bank {
    PayPal,
    BOFA,
    AmazonPay,
}

impl std::fmt::Display for Bank {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Bank::PayPal => write!(f, "PayPal"),
            Bank::BOFA => write!(f, "BOFA"),
            Bank::AmazonPay => write!(f, "AmazonPay"),
        }
    }
}

#[derive(Debug)]
pub struct PaymentData {
    pub amount: Decimal,
    pub transaction_id: String,
    pub bank: Bank,
}

#[derive(Debug)]
pub enum GetDBErr {
    LockerSameAsActive,
    InvalidUserLocker,
    LockerTooManyPackages,
    LockerWeightTooBig(Decimal),

    InvalidUserBranch,

    InvalidUserDelivery(u8),
    NoCompatBranchDelivery,
}