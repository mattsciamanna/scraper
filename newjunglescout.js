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
    await driver.sleep(6000);
    // CHANGE EACH RUNTHROUGH industrial and scientific or whatever 
    // await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[17]/svg/rect')).click()
    
    // // no need to change, click on fba then fbm
    // await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/svg/g')).click()
    // await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/div[2]/svg/g')).click()

    // // NO NEED TO CHANGE, MAX SELLERS > MIN REVIEWS > MAX SALES > MIN SALES
    await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div[8]/input[2]')).sendKeys('1')
    await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/input[1]')).sendKeys('1')
    await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div[7]/input[2]')).sendKeys('500')
    await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div[7]/input[1]')).sendKeys('6')
    // you need to check shit yoself here. 
    await driver.sleep(2000);
    await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[1]/div[4]/div[2]/button[2]')).click()
    await driver.sleep(4000);

    // on junglescout at this point 
    var moreRows = true;
    var pageNumber = 0;
    while (moreRows){
        console.log(pageNumber);
        
        // start actual scrape
        var rows = await driver.findElements(By.css(".table__row"));
        
        // should find button, scroll to it, click it .
        exportButton = await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[3]/div[1]/button'));
        // console.log(exportButton)

        // first we scroll the button into view, but then we say fuck it because its covered by the navbar so we scroll back up a bit.
        await driver.executeScript("arguments[0].scrollIntoView(true);", exportButton);
        await driver.executeScript("window.scrollBy(0,-300)");
        await exportButton.click();
        driver.sleep(500);

        // var results = await [];
        // for (row of rows){
        //     var attributes = await row.findElements(By.css('.table__cell__section--text'));
        //     var index = await 0;
        //     var datum = await {};
        //     for(attribute of attributes){
        //         var value = await attribute.getAttribute('innerHTML');
        //         datum[index] = await value;
        //         index = await index + 1;
        //     }
        // //     await results.push(datum);
        // }
        // scroll to bottom
        await driver.executeScript("window.scrollTo(0, document.body.scrollHeight)");


        // click next page, iterate pageNumber
        await driver.findElement(By.xpath('//*[@id="app-content"]/div/div[3]/ul/li[9]')).click();
        await driver.sleep(8000);
        pageNumber = await pageNumber + 1;

        // break condition
        if (pageNumber == 25){
            moreRows = false; 
        }

        // getting rid of this pry
        // await csvWriter.writeRecords(results);
    }
    
  } finally {
      console.log('DID EVERYTHING THAT IT SHOULD HAVE DONE');
    //   await driver.quit();
    // await driver.quit();
  }
};
example();


