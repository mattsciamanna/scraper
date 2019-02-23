const {Builder, By, Key, until} = require('selenium-webdriver');

// csv stuff
const csv = require('csv');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;


async function example() {
  let driver = await new Builder().forBrowser('chrome').build();
  try {
    await driver.get('https://members.junglescout.com/#/login');
    await driver.findElement(By.xpath('//input[@label="email"]')).sendKeys('mattsciamanna123@gmail.com');
    await driver.findElement(By.xpath('//input[@label="password"]')).sendKeys('Friendship69', Key.RETURN);
    await driver.sleep(1000);
    await driver.get('https://members.junglescout.com/?_ga=2.267842058.547866213.1542953084-1549179723.1542953084#/database');
    await driver.sleep(10000);

    var moreRows = true;
    var pageNumber = 0;
    while (moreRows){
        console.log(pageNumber);
        const csvWriter = createCsvWriter({
            // changed for scrapehierarchy,  original => path: './with_images.csv'
            path: './final' + String(pageNumber) + '.csv', // parse int because need to pass string this is where to use process.argv[1] to append to the end of the file name
            header: [{id:'0', title:'ASIN'}, {id:'1', title:'category'}, {id:'2', title:'brand'}, {id:'3', title:'seller'}, {id:'4', title:'weight'}, {id:'5', title:'blank'}, {id:'6', title:'BSR'}, {id:'7', title:'Num Sellers'}, {id:'8', title:'LQS'}, {id:'9', title:'nine'},{id:'10', title:'ten'},]
        });
        
        // start actual scrape
        var rows = await driver.findElements(By.css(".table__row"));
        
        var results = await [];
        for (row of rows){
            var attributes = await row.findElements(By.css('.table__cell__section--text'));
            var index = await 0;
            var datum = await {};
            for(attribute of attributes){
                var value = await attribute.getAttribute('innerHTML');
                datum[index] = await value;
                index = await index + 1;
            }
            await results.push(datum);
        }
        // scroll to bottom
        await driver.executeScript("window.scrollTo(0, document.body.scrollHeight)");


        // click next page, iterate pageNumber
        await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[3]/ul/li[9]')).click();
        await driver.sleep(10000);
        pageNumber = await pageNumber + 1;

        // break condition
        if (pageNumber == 24){
            moreRows = false; 
        }

        // little update to our csv
        await csvWriter.writeRecords(results);
    }
    
  } finally {
      console.log('DID EVERYTHING THAT IT SHOULD HAVE DONE');
    //   await driver.quit();
    // await driver.quit();
  }
};
example();





// // table_element = await driver.findElement(By.id("table--database"));
    // // for now just fuck with one, fix later 
    // tr_collection = await driver.findElements(By.css(".table__row"));
    // asin = [];
    // console.log("boutta do it");
    // values = await tr_collection.findElements(By.css('.table__cell__section--text')).getAttribute('innerHTML');
    // // finaltry = tr_collection.findElement(By.xpath("//div[@class='table__cell__section--actionable']")).innerHTML();
    // console.log(values);
    // // for each
    // tr_collection.values.forEach(row => {
    //     textPromise = row.findElement(By.xpath("//div/div[1]/div[1]/div[1]"));
    //     textPromise.then((text) => {
    //         console.log(text);
    //         });
    //   });

    // // List<WebElement>
    // console.log(tr_collection);
    
    
    // // rows = await driver.findElement(By.xpath('//div[@class="table__row"]'));
    // // console.log(rows);



// async function example2() {
//     let driver = await new Builder().forBrowser('chrome').build();
//     try {
//       await driver.get('https://www.amazon.com/ap/signin?openid.return_to=https%3A%2F%2Faffiliate-program.amazon.com%2Fhome%2Freports%2Fdownload%3Fstore_id%3Dtudhywbrgyg-20%26file%3D1530959191376-Fee-Tracking-46898254-89c9-4022-8784-2c20c3869170-CSV.csv.zip%26name%3DFee-Tracking-07Jul2018-032631.zip&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_associates_us&openid.mode=checkid_setup&marketPlaceId=ATVPDKIKX0DER&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.pape.max_auth_age=0');
//       await driver.findElement(By.name('email')).sendKeys('russell.pekala@gmail.com');
//       await driver.findElement(By.name('password')).sendKeys('M!311!thon3', Key.RETURN);
//       // Downloads file somewhere.  TODO: Find default download location.  Fuck with that a bit.
  
  
//     } finally {
//         console.log('DID EVERYTHING THAT IT SHOULD HAVE DONE');
//       // await driver.quit();
//     }
//   };
  
  
  // var webdriver = require('selenium-webdriver');
// var chrome = require('selenium-webdriver/chrome');
// var path = require('chromedriver').path;

// var service = new chrome.ServiceBuilder(path).build();
// chrome.setDefaultService(service);


// var browser = new webdriver.Builder().withCapabilities(webdriver.Capabilities.chrome()).build();


// browser.get('http://www.google.com');

// var promise = browser.getTitle();

// promise.then(function(title) {
//     console.log(title);
// });

// browser.quit();




    // await driver.findElement(By.name('password')).sendKeys('M!311!thon3', Key.RETURN);
    // tuba = await driver.findElement(By.xpath('//*[@id="table--database"]/div/div[2]'));
    // console.log(tuba);
    // console.log('tuba');
    // .sendKeys('russell.pekala');
    // await driver.findElement(By.name('password')).sendKeys('M!311!thon3', Key.RETURN);
    // await driver.findElement(By.css('#ac-report-download-launcher')).click();
    // await driver.wait(until.elementLocated(By.css('#ac-reports-download-generate-announce')), 20000);
    // await console.log('New modal thing has loaded');
    // await driver.findElement(By.css(".ac-report-download-format>.a-form-horizontal>span:nth-child(2) input")).sendKeys(Key.RETURN);  // No error but didn't work
    // await driver.findElement(By.css(".ac-report-download-format>.a-form-horizontal>span:nth-child(2) i")).click();  // Does not work
    // await driver.findElement(By.css("#ac-reports-download-generate-announce")).click();

    // 


    //used to work -- - - 
    
    // var rows = await driver.findElements(By.css(".table__row"));
    // for (row of rows){
    //   var attributes = await row.findElements(By.css('.table__cell__section--text'));
    //   for(attribute of attributes){
    //     var value = await attribute.getAttribute('innerHTML');
    //     console.log(value);
    //   }
    // }