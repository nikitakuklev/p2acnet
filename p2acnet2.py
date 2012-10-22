 
import requests
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class P2ACNETGroup(object):

    def __init__(self, channel_list, start_time, end_time):
        self.channel_list = channel_list
        self.start_time = start_time
        self.end_time = end_time
        
    def run_group(self):
        data_dict = {}
        for channel in self.channel_list:
            new_instance = P2ACNET(channel, self.start_time, self.end_time)
            data_dict[channel] = new_instance.parse_query()
        return data_dict

    def plot_group(self, data_dict, xlabel="", ylabel=""):
        '''
        I want to make this run over the plot_single of P2ACNET class, though I'm not sure how to implement.
        This would reflect the run_group methodology and be more consistent
        '''
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for channel in data_dict:
            times = data_dict[channel][:,0]
            values = data_dict[channel][:,1]
            ax.plot_date(times, values, '-', label=channel)
        ax.autoscale_view()
        fig.autofmt_xdate()        
        plt.legend().get_frame().set_alpha(.5)
        title = str("Start ="+ self.start_time+ ", End ="+ self.end_time)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()
        return
            
            

class P2ACNET(object):
    '''
    This class uses the iter_lines() requests method to iterate over each line of the returned content
    instead of loading the whole response into memory and then performing operations on it. Also,
    this version does not convert the datetime elements into matplotlib date types in parse_query. (This
    seemed to be the cause of significant slowdown)
        
    '''

    def __init__(self, channel, start_time, end_time, node = 'fastest'):
        self.channel = channel
        self.start_time = start_time
        self.end_time = end_time
        self.node = node
        geturl = 'http://www-ad.fnal.gov/cgi-bin/acl.pl?acl=logger_get/double/node='\
                       + self.node + '/start='+ self.start_time + '/end='+ self.end_time + '+' + self.channel
        self.r = requests.get(geturl, prefetch=False)
        print "\tQuery to", self.channel, "successful"
        print "HTTP get status: ", self.r.status_code
        # print "HTTP error? ", r.raise_for_status()
        
    def parse_query(self):
        print "\tParsing returned content..."
        data_list = []
        for element in self.r.iter_lines():
            data_split = element.split('  ')
            datetime_el = mdates.date2num(dt.datetime.strptime(data_split[0], '%d-%b-%Y %H:%M:%S.%f'))
            value_el = float(data_split[1].strip())
            data_list.append([datetime_el, value_el])
        self.data_array = np.array(data_list)
        print "\tNumber of returned time-value pairs:", self.data_array.shape[0]
        return self.data_array

    def plot_single(self, data_array):
        times = data_array[:,0]
        values = data_array[:,1]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot_date(times, values, '-')
    #----Options to manually format the tics--------------------------#
    # ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%M-%d %H:%S'))
    # # ax.xaxis.set_minor_locator(mdates.HourLocator())
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
        ax.autoscale_view()
        fig.autofmt_xdate()
        #plt.show()
        return fig
    
if __name__ == '__main__':
    #-------------Test multiple channels using P2ACNETGroup-----------#
    channel_list = ['G:OUTTMP']
    query1 = P2ACNETGroup(channel_list, '17-SEP-2012-7:30', '17-OCT-2012-8:30')
    plot = query1.plot_group(query1.run_group())
    
    
    #------Test single plot-----------#
    # channel = 'E:HTC05'
    # start_time = '10-OCT-2012-12:30'
    # end_time = '17-OCT-2012-14:30'
    # instance = P2ACNET(channel, start_time, end_time)
    # plot = instance.plot_single(instance.parse_query())
    # plt.show(plot)
    

    
