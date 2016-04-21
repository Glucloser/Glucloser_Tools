
require 'selenium-webdriver'

def setup
    profile = Selenium::WebDriver::Firefox::Profile.ini()['Selenium']
    @driver = Selenium::WebDriver.for :firefox, :profile=>profile
end

def teardown
    @driver.quit
end

def run
    setup
      yield
        teardown
end

run do
    @driver.navigate.to 'https://carelink.minimed.com/patient/entry.jsp'
    @driver.find_element(:id, 'j_username').send_keys ENV['carelink_user']
    @driver.find_element(:id, 'j_password').send_keys ENV['carelink_pw']
    @driver.find_element(:id, 'loginButton').click

    begin
    Selenium::WebDriver::Wait.new(:timeout => 10).until { @driver.find_element(:id, 'toReports')}
    rescue Selenium::WebDriver::Error::TimeOutError
      @driver.save_screenshot('error0.png')
    end
    @driver.find_element(:id, 'toReports').click

    begin
    Selenium::WebDriver::Wait.new(:timeout => 10).until { @driver.find_element(:id, 'originalReportsLink')}
    rescue Selenium::WebDriver::Error::TimeOutError
      @driver.save_screenshot('error2.png')
    end
    @driver.find_element(:id, 'originalReportsLink').click

    begin
    Selenium::WebDriver::Wait.new(:timeout => 10).until { @driver.find_element(:link, 'Data Export (CSV)')}
    rescue Selenium::WebDriver::Error::TimeOutError
      @driver.save_screenshot('error1.png')
    end
    @driver.find_element(:link, 'Data Export (CSV)').click
    @driver.find_element(:css, '#reportPicker11 > span.reportNav_right > #reportNav_button').click
end
