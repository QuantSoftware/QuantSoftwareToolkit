package com;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Writer;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.TimeZone;

public class Main {


	/**
	 * @param args
	 * @throws InterruptedException 
	 * @throws NumberFormatException 
	 * @throws IOException 
	 */
	public static void main(String[] args) throws NumberFormatException, InterruptedException, IOException {
		// TODO Auto-generated method stub

		int dataUpdaterHour= 18; //MUST be in 24 hr time
		int dataUpdateMinute= 0;
		//int timezoneOffsetHour= 4; //+4 for ET. +ve if local time is behind GMT. -ve if local time is ahead of GMT.
		//long currentTime;
		long millisToStartAt;
		final long MILLIS_PER_DAY=86400*1000;

		Calendar cal= Calendar.getInstance();
		////		SimpleDateFormat sdf= new SimpleDateFormat ("HH");
		String currentHour, currentMinute, line;
		//		
		final String dataUpdaterTask="C:\\installations\\Trading Applications\\bin\\DataUpdater.exe autoupdate=1 autoclose=1";
		final String dataConverterTask="C:\\installations\\Premium Data Converter\\Premium Data Converter.exe autostart=1 autoclose=1";
		final String csvToHdfConverterTask= "C:\\installations\\Python26\\python.exe C:\\workspace\\Backtester1\\src\\csvconverter\\csvapi.py ";//space at the end is important
		//final String csvToHdfConverterTask= "C:\\installations\\Python26\\python.exe C:\\workspace\\Trial\\src\\Trial.py ";//space at the end is important
		final String logFilepath= "C:\\logs\\";
		final String masterLogFileName= "master_log";


		Process process;
		BufferedReader br;
		BufferedWriter out = null;
		File logFile= null;
		File masterLogFile=null;
		Writer outputWriter= null;
		Writer masterOutputWriter=null;

		cal= Calendar.getInstance();
		TimeZone timeZone= TimeZone.getDefault();
		masterLogFile= new File (logFilepath+ masterLogFileName+(new SimpleDateFormat("dd-MM-yyyy HH-mm")).format(cal.getTime())+ ".txt");
		masterLogFile.createNewFile();
		masterOutputWriter= new BufferedWriter (new FileWriter(masterLogFile));


		millisToStartAt= (long) (MILLIS_PER_DAY* Math.floor(System.currentTimeMillis() / MILLIS_PER_DAY)) + ((dataUpdaterHour)*60*60*1000 )+ (dataUpdateMinute*60*1000) - (timeZone.getOffset(System.currentTimeMillis()));
		//Math.floor(System.currentTimeMillis() / MILLIS_PER_DAY) give the timestamp of the midnight that already happened. This is the midnight between yesterday and today.
		
		display("millisToStartAt " + millisToStartAt + " currentMillis: "+ System.currentTimeMillis(), masterOutputWriter);


		if (millisToStartAt > System.currentTimeMillis()){
			display("Sleeping for about " + (millisToStartAt - System.currentTimeMillis()) + " millisecs.", masterOutputWriter);
			Thread.sleep(millisToStartAt- System.currentTimeMillis());
			display("Slept well. Back to work now...", masterOutputWriter);
			millisToStartAt-= MILLIS_PER_DAY; //hack for testing so that if this is started before the due time- then it starts at the time again...
		}
		else{
			//Update time today is already past, so might as well update right away..
			//No need to sleep. 
			display("Update time today is already past so updating right away...", masterOutputWriter);
		}

		while (Boolean.TRUE){
			
			cal= Calendar.getInstance(); 
			display("Deleting all CSV files", masterOutputWriter);
			//not deleting C:\Trading data text\Stocks\US\Indices or anything in it
			deleteAllFiles("C:\\Trading data text\\Stocks\\Delisted Securities\\US Recent", masterOutputWriter);
			deleteAllFiles("C:\\Trading data text\\Stocks\\US\\AMEX", masterOutputWriter);
			deleteAllFiles("C:\\Trading data text\\Stocks\\US\\Delisted Securities", masterOutputWriter);
			deleteAllFiles("C:\\Trading data text\\Stocks\\US\\NASDAQ", masterOutputWriter);
			deleteAllFiles("C:\\Trading data text\\Stocks\\US\\NYSE", masterOutputWriter);
			deleteAllFiles("C:\\Trading data text\\Stocks\\US\\NYSE Arca", masterOutputWriter);
			deleteAllFiles("C:\\Trading data text\\Stocks\\US\\OTC", masterOutputWriter);
			
			//Data Updater
			cal= Calendar.getInstance(); 
			display("Starting data updater at " + (new SimpleDateFormat("dd-MM-yyyy HH:mm:ss")).format(cal.getTime()), masterOutputWriter);
			//currentTime= System.currentTimeMillis();
			process= Runtime.getRuntime().exec(dataUpdaterTask);
			process.waitFor();

			//Proprietory to CSV converter
			cal= Calendar.getInstance();
			display("Starting Data converter at " + (new SimpleDateFormat("dd-MM-yyyy HH:mm:ss")).format(cal.getTime()), masterOutputWriter);
			process= Runtime.getRuntime().exec(dataConverterTask);
			process.waitFor();

			//CSV to HDF converter
			cal= Calendar.getInstance();
			display("Converting from CSV to HDF at " + (new SimpleDateFormat("dd-MM-yyyy HH:mm:ss")).format(cal.getTime()), masterOutputWriter);
			process= Runtime.getRuntime().exec(csvToHdfConverterTask+ (new SimpleDateFormat("yyyyMMdd")).format(cal.getTime()));// pass the end date as the parameter
			br = new BufferedReader( new InputStreamReader (process.getInputStream()));

			//logFile= new File (logFilepath+ (new SimpleDateFormat("dd-MM-yyyy HH:mm:ss")).format(cal.getTime())+ ".txt");
			logFile=null;
			logFile= new File (logFilepath+ (new SimpleDateFormat("dd-MM-yyyy HH-mm")).format(cal.getTime())+ ".txt");

			//logFile= new File (logFilepath+ "blah.txt");
			logFile.createNewFile();
			outputWriter= new BufferedWriter (new FileWriter(logFile));



			while ((line= br.readLine())!=null){
				//System.out.println(line); //Uncomment to see the output on command line
				outputWriter.write(line+"\n");
			}

			process.waitFor();
			outputWriter.flush();
			outputWriter.close();
			br.close();

			millisToStartAt= (long) (MILLIS_PER_DAY* Math.ceil(System.currentTimeMillis() / MILLIS_PER_DAY)) + ((dataUpdaterHour)*60*60*1000 )+ (dataUpdateMinute*60*1000) - (timeZone.getOffset(System.currentTimeMillis()));
			//note subtle but important difference from earlier line. This is Math.ceil- which gives the timestamp at midnight that will happen between today and tomorrow 
			
			//change master log file here
			if (millisToStartAt - System.currentTimeMillis() > 0){
				display("*********************** \nSleeping for about a day \n*********************** approx:" + (millisToStartAt- System.currentTimeMillis()), masterOutputWriter);
				//finishing up on old file
				masterOutputWriter.flush();
				masterOutputWriter.close();
				
				Thread.sleep(millisToStartAt - System.currentTimeMillis());
				//I thought it makes sense to change the log file only if it slept- and not change if it did not sleep
				//now starting new file
				cal= Calendar.getInstance();
				masterLogFile= new File (logFilepath+ masterLogFileName+(new SimpleDateFormat("dd-MM-yyyy HH-mm")).format(cal.getTime())+ ".txt");
				masterLogFile.createNewFile();
				masterOutputWriter= new BufferedWriter (new FileWriter(masterLogFile));
				display("Ah! Feels nice to wake up after a day \n***********************", masterOutputWriter);
			}
			else{
				display("NOTE: The process took more than 24 hours to complete. Not pretty. Good luck.", masterOutputWriter);
			}

		}

	}

	public static void display (String str, Writer writer) throws IOException{
		System.out.println(str);
		writer.write("\n"+str);
		writer.flush();
	}

	/*
	 * Does not delete folders inside the given path. Leaves them untouched.
	 */
	public static void deleteAllFiles(String pathToDir, Writer writer) throws IOException{
		
		File folder= new File (pathToDir);
		File[] files= folder.listFiles();
		
		
		
		//Assuming that there are no directories here
		for (int i=0; i< files.length; i++){
			if (files[i].isFile()){
				if (!files[i].delete()){
					display("ERROR:Unable to delete "+ files[1].getPath(), writer);
				}
			}
		}
		
		
		
	}

}
