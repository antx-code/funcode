const puppeteer = require('puppeteer');
const xl = require('xlsx');
const readline = require('readline');

const login_url = 'https://steamcommunity.com/login/home/?goto=';
const market_url = 'https://steamcommunity.com/market/';
const search = 'search?q=';

const USERNAME = 'lovehouxiaomao';
const PASSWD = 'qq136571820luoran111';

var g_names = [];
var g_prices = [];
var g_nums = [];

//创建readline接口实例
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const question = (query) => new Promise(resolve => rl.question(query, (answer) => resolve(answer)));

function read_excel() {
    const workbook = xl.readFile('表格.xls');
    const sheetName = workbook.SheetNames;
    const worksheet = workbook.Sheets[sheetName[0]];
    let ass = worksheet['!ref'];
    // console.log(ass);
    var ran = ass.toString().split(':')[1].split('C')[1];
    console.log('共有'+ran+'个待求购商品');
    for (k=1;k<+ran;k++){
        let name = worksheet['A'+(k+1).toString()];
        let num = worksheet['B'+(k+1).toString()];
        let price = worksheet['C'+(k+1).toString()];
        g_names.push(name.v);
        g_nums.push(num.v);
        g_prices.push(price.v);
    }
    // console.log(typeof g_nums[2]);
}

(async () => {
    const browser = await (puppeteer.launch({
        // executablePath:'',
        headless:true,
        slowMo :50,
        timeout:0,
        defaultViewport :{
            width: 1280,
            height: 800},
        args:[
          '--disable-extensions',
          '--hide-scrollbars',
          '--disable-gpu',
          '--mute-audio',
        ],
    }));
    const page = await browser.newPage();
    await read_excel();

    await page.goto(login_url,{waituntil: 'load',timeout:0}); // 进行登录
    const username = await question('请输入Steam账号：');
    await page.type('[id="steamAccountName"]',username);
    const passwd = await question('请输入Steam密码：');
    await page.type('[id="steamPassword"]',passwd);
    await page.click('[id="SteamLogin"]');
    await page.waitFor(3000);

    const fa2 = await question('请输入2FA:');
    await page.type('[id="twofactorcode_entry"]',fa2);
    await page.keyboard.press('Enter');
    await page.waitForNavigation({waituntil:'[class="btn_profile_action btn_medium"]',timeout:0});
    await console.log('登录成功......');

    for (k=0;k<g_names.length;k++) {
        await console.log('准备执行第'+(k+1).toString()+'个商品过程');
        await console.log('求购商品名称:「'+g_names[k]+'」---求购价格:「¥'+g_prices[k].toString()+'」---求购数量:「'+g_nums[k].toString()+'」');
        await page.goto(market_url + search + g_names[k]);  // 进入Market页面进行搜索
        await page.click('[id="result_0_name"]');    // 选择需要的商品
        await page.waitFor(3000);
        const isCanbuy = await page.$('[class="btn_green_white_innerfade btn_medium market_noncommodity_buyorder_button"]');
        if (isCanbuy){
            await page.click('[class="btn_green_white_innerfade btn_medium market_noncommodity_buyorder_button"]'); // 提交订单
        } else {
            // await console.log('特殊按钮');
            await page.click('[class="btn_green_white_innerfade btn_medium market_commodity_buy_button"]')[0];
        }
        
        await page.waitFor(4000);
        await page.click('[id="market_buy_commodity_input_price"]');
        for (i=0;i<5;i++){  // 移动到最右边
            await page.keyboard.press('ArrowRight');
        }
        for (i = 0; i < 10; i++) {
            await page.keyboard.press('Backspace');
        };
        // await page.waitFor(1000);
        await page.type('[id="market_buy_commodity_input_price"]', g_prices[k].toString());
        await page.click('[id="market_buy_commodity_input_quantity"]');
        await page.keyboard.press('ArrowRight');
        await page.keyboard.press('Backspace');
        // await page.waitFor(1000);
        await page.type('[id="market_buy_commodity_input_quantity"]', g_nums[k].toString());
        await page.click('[id="market_buyorder_dialog_accept_ssa"]');
        await page.click('[id="market_buyorder_dialog_purchase"]');
        await console.log('第'+(k+1).toString()+'个求购订单完成...');
        await page.waitFor(7000);
    }
    await console.log('所有求购订单已完成...');
    await page.waitFor(7000);
    await browser.close();
})();
