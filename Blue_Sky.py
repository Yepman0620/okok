    @staticmethod
    def security_open(expression, timestamps, resolution_secur=120, resolution_expr=30):
        t_base = dt(2017, 7, 2, 8, 0, 0)  # according to TradingView chart (EOS).
        t_ofs = dt.fromtimestamp(timestamps[0])
        time_lap = t_ofs - t_base
        minuets_lap, seconds_lap = divmod(time_lap.days * 86400 + time_lap.seconds, 60)
        minuets_ofs = resolution_secur - minuets_lap % resolution_secur
        minuets_ofs = int(minuets_ofs / resolution_expr)

        ret_expr = []
        for idx in range(0, minuets_ofs):
            last_val = expression[minuets_ofs]
            ret_expr.append(last_val)

        cycle_len = resolution_secur / resolution_expr

        src_lenth = len(expression)
        for idx in range(minuets_ofs, src_lenth):
            cur_cycle_idx = int((idx - minuets_ofs) / cycle_len)

            last_val = expression[int(cycle_len * cur_cycle_idx + minuets_ofs)]
            ret_expr.append(last_val)

        return ret_expr


    @staticmethod
    def security_close(expression, timestamps, resolution_secur=120, resolution_expr=30):
        t_base = dt(2017, 7, 2, 8, 0, 0)  # according to TradingView chart (EOS).
        t_ofs = dt.fromtimestamp(timestamps[0])
        time_lap = t_ofs - t_base
        minuets_lap, seconds_lap = divmod(time_lap.days * 86400 + time_lap.seconds, 60)
        minuets_ofs = resolution_secur - minuets_lap % resolution_secur
        minuets_ofs = int(minuets_ofs / resolution_expr)

        ret_expr = []
        for idx in range(0, minuets_ofs):
            last_val = expression[minuets_ofs]
            ret_expr.append(last_val)

        cycle_len = int(resolution_secur / resolution_expr)

        src_lenth = len(expression)
        for idx in range(minuets_ofs, src_lenth):
            cur_cycle_idx = int((idx - minuets_ofs) / cycle_len)

            idx_ = int(cycle_len * (cur_cycle_idx + 1) + minuets_ofs) - 1
            if idx_ > src_lenth - 1:
                # idx_ -= 4
                idx_ = src_lenth - 1
            last_val = expression[idx_]
            ret_expr.append(last_val)

        return ret_expr


    def strategy_occ(self, csv_file_name, data, window_size=30, rng=120, unit=30):
        close_ema = get_ema(csv_file_name, 'close', window_size)
        open_ema = get_ema(csv_file_name, 'open', window_size)

        secur_close = self.security_close(close_ema[:, 1], data[:, 0], rng, unit)
        secur_open = self.security_open(open_ema[:, 1], data[:, 0], rng, unit)

        buys, sells, _, _, _ = self.backtest(secur_close, secur_open, data, int(rng / unit), 2)
        return buys, sells

    def strategy_test_occ_draw(self, csv_file_name, data, window_size, rng, unit, lever):
        # open, close, low, high = self.get_hlco(data)
        close_ema = get_ema(csv_file_name, 'close', window_size)
        open_ema = get_ema(csv_file_name, 'open', window_size)

        secur_close = self.security_close(close_ema[:, 1], data[:, 0], rng, unit)
        secur_open = self.security_open(open_ema[:, 1], data[:, 0], rng, unit)

        self.backtest(secur_close, secur_open, data, int(rng / unit), lever, draw=True)

        open_column, close, low, high = self.get_hlco(data)
        timestamp = data[:, 0]
        timestamp_ = []
        for ts in timestamp:
            timestamp_.append(dt.fromtimestamp(ts))
        timestamp_ = mdates.date2num(timestamp_)
        data_list = []
        open_len = open_column.size

        for idx in range(0, open_len):
            datas = (timestamp_[idx], open_column[idx], high[idx], low[idx], close[idx])
            data_list.append(datas)

        # plot ref: https://zhuanlan.zhihu.com/p/29519040
        plt.figure(facecolor='#07000d', figsize=(20, 16))  # fig =
        ax1 = plt.subplot2grid((6, 4), (0, 0), rowspan=6, colspan=4, axisbg='#07000d')
        mpf.candlestick_ohlc(ax1, data_list, width=.01, colorup='#53c156', colordown='#ff1717')
        ax1.plot(timestamp_, secur_close, '#00ff00', label='close', linewidth=1.1)
        ax1.plot(timestamp_, secur_open, '#ff0000', label='open', linewidth=1.1)
        ax1.grid(True, color='w')
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%H:%M:%S'))

        ax1.yaxis.label.set_color("w")
        ax1.spines['bottom'].set_color("#5998ff")
        ax1.spines['top'].set_color("#5998ff")
        ax1.spines['left'].set_color("#5998ff")
        ax1.spines['right'].set_color("#5998ff")
        ax1.tick_params(axis='y', colors='w')
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax1.tick_params(axis='x', colors='w')
        plt.ylabel('Price')

        secure_len = secur_close.__len__()
        secure_dff = []
        for i in range(0, secure_len):
            secure_dff.append(secur_close[i] - secur_open[i])
        d = scipy.zeros(secure_len)

        plt.fill_between(timestamp_, secur_close, secur_open, where=secure_dff > d, color='green', alpha='1.0')
        plt.fill_between(timestamp_, secur_close, secur_open, where=secure_dff < d, color='red', alpha='1.0')

        plt.show()

    def draw_strategy(self, period_len, tok_name, unit_time, lever, window, rng):
        unit = self.unit_time_dict[unit_time]
        # csv_file_name = os.path.join('data', "{}{}{}".format(tok_name + '_' + unit_time + "_", period_len, ".csv"))
        # print(csv_file_name)
        # if not os.path.isfile(self.symbol_data_csv[tok_name]):
        self.refresh_symbol_data(symbol=tok_name, size=period_len)
        # data_matrix = get_kline_matrix(symbol=tok_name, unit_time=unit_time, size=period_len)
        # else:
        #     with open(csv_file_name[:-4] + '.pickle', 'rb') as handle:
        #         data_matrix = pickle.load(handle)
        self.strategy_test_occ_draw(self.symbol_data_csv[tok_name], self.symbol_kline[tok_name],
                                    window, rng, unit, lever)