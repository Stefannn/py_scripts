{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "PyHEADTAIL v1.4.1-19-g198c5df2bd\n",
      "\n",
      "\n"
     ]
    }
   ],
   "source": [
    "import sys\n",
    "sys.path.append(\"../\")\n",
    "%matplotlib tk\n",
    "\n",
    "import numpy as np\n",
    "from scipy.constants import c, e, m_p\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "\n",
    "import PyCERNmachines.CERNmachines as m\n",
    "from PySUSSIX import Sussix\n",
    "\n",
    "from PyHEADTAIL.spacecharge.transverse_spacecharge import TransverseSpaceCharge\n",
    "from PyHEADTAIL.field_maps.Transverse_Efield_map import Transverse_Efield_map\n",
    "\n",
    "from PyPIC.FFT_OpenBoundary_SquareGrid import FFT_OpenBoundary_SquareGrid\n",
    "from PyHEADTAIL.particles.slicing import UniformBinSlicer\n",
    "\n",
    "from mpl_toolkits.mplot3d import Axes3D\n",
    "from matplotlib import cm\n",
    "from PyHEADTAIL.particles.generators import ParticleGenerator, gaussian2D_asymmetrical\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### tune analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def tune_analysis(bunch, machine, x_i, xp_i, y_i, yp_i):\n",
    "\t\tn_turns = x_i.shape[1]\n",
    "\n",
    "\t\tqx_i = np.empty(bunch.macroparticlenumber)\n",
    "\t\tqy_i = np.empty(bunch.macroparticlenumber)\n",
    "\n",
    "\t\tspectrum_x = np.abs(np.fft.fft(x_i, axis = 1))[:,:n_turns/2]\n",
    "\t\ttune_peak_x = np.float_(np.argmax(spectrum_x, axis=1))/float(n_turns)\n",
    "\n",
    "\t\tspectrum_y = np.abs(np.fft.fft(y_i, axis = 1))[:,:n_turns/2]\n",
    "\t\ttune_peak_y = np.float_(np.argmax(spectrum_y, axis=1))/float(n_turns)\n",
    "\n",
    "\t\tprint 'analysing particle spectra ... this may take some time.'\n",
    "\t\tfor p_idx in xrange(bunch.macroparticlenumber):\n",
    "\t\t\t\n",
    "\t\t\tSX = Sussix()\n",
    "\t\t\tSX.sussix_inp(nt1=1, nt2=n_turns, idam=2, ir=0, tunex=tune_peak_x[p_idx], tuney=tune_peak_y[p_idx])\n",
    "\n",
    "\t\t\tSX.sussix(x_i[p_idx,:], xp_i[p_idx,:],\n",
    "\t\t\t\t\t  y_i[p_idx,:], yp_i[p_idx,:],\n",
    "\t\t\t\t\t  x_i[p_idx,:], xp_i[p_idx,:]) \n",
    "\t\t\tqx_i[p_idx] = SX.ox[0]\n",
    "\t\t\tqy_i[p_idx] = SX.oy[0]\n",
    "\t\t\t\n",
    "\t\t\tsys.stdout.write('\\rparticle %d'%p_idx)\n",
    "\t\t\t\t\n",
    "\t\tx_centroid = np.mean(x_i, axis=0)\n",
    "\t\txp_centroid = np.mean(xp_i, axis=0)\n",
    "\t\ty_centroid = np.mean(y_i, axis=0)\n",
    "\t\typ_centroid = np.mean(yp_i, axis=0)\n",
    "\t\t\n",
    "\t\t#print x_centroid.shape\n",
    "\n",
    "\t\tSX = Sussix()\n",
    "\t\tSX.sussix_inp(nt1=1, nt2=n_turns, idam=2, ir=0, tunex=machine.Q_x%1, tuney=machine.Q_y%1)\n",
    "\t\tSX.sussix(x_centroid, xp_centroid,\n",
    "\t\t\t\t  y_centroid, yp_centroid,\n",
    "\t\t\t\t  x_centroid, xp_centroid) \n",
    "\t\tqx_centroid = SX.ox[0]\n",
    "\t\tqy_centroid = SX.oy[0]\n",
    "\n",
    "\t\treturn qx_i, qy_i, qx_centroid, qy_centroid\n",
    "    \n",
    "def plot_tune_spread(machine, qx_i, qy_i, qx_centroid, qy_centroid):\n",
    "    plt.plot(np.abs(qx_i), np.abs(qy_i), '.')\n",
    "    plt.plot([np.modf(machine.Q_x)[0]], [np.modf(machine.Q_y)[0]], 'ro', label='Bare tune')\n",
    "    #if flag_initial_displacement:\n",
    "    #    plt.plot([np.abs(qx_centroid)], [np.abs(qy_centroid)], 'xg', markersize = 10, label='Coherent tune')\n",
    "    #plt.plot([.15, .30], [.15, .30], 'k')\n",
    "    plt.legend(loc='lower right')\n",
    "    plt.xlabel('$Q_x$');plt.ylabel('$Q_y$')\n",
    "    plt.axis('equal')\n",
    "    plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### define the machine (PS) and create a matched gaussian bunch"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Synchrotron init. From kwargs: charge = 1.602176565e-19\n",
      "Synchrotron init. From kwargs: mass = 1.672621777e-27\n",
      "Synchrotron init. From kwargs: Q_y = 6.27\n",
      "Synchrotron init. From kwargs: n_segments = 20\n",
      "Synchrotron init. From kwargs: gamma = 2.49\n",
      "Synchrotron init. From kwargs: Q_x = 6.35\n"
     ]
    }
   ],
   "source": [
    "macroparticlenumber = 2000\n",
    "macroparticlenumber_for_field_calculation = 1000000\n",
    "charge    = e\n",
    "mass      = m_p\n",
    "n_turns = 128\n",
    "\n",
    "machine = m.PS(Q_x=6.35, Q_y=6.27, gamma=2.49, n_segments=20, longitudinal_focusing='linear', charge=charge, mass=mass)\n",
    "\n",
    "intensity = 160e10/2\n",
    "epsn_x    = 2.5e-6\n",
    "epsn_y    = 2.5e-6\n",
    "sigma_z   = 180e-9 /4 * (machine.beta * c)\n",
    "\n",
    "bunch = machine.generate_6D_Gaussian_bunch(n_macroparticles=macroparticlenumber, intensity=intensity,\n",
    "                                          epsn_x=epsn_x, epsn_y=epsn_y, sigma_z=sigma_z)\n",
    "bunch_for_field = machine.generate_6D_Gaussian_bunch(n_macroparticles=macroparticlenumber_for_field_calculation,\n",
    "                                                     intensity=intensity,\n",
    "                                          epsn_x=epsn_x, epsn_y=epsn_y, sigma_z=sigma_z)\n",
    "\n",
    "# store the initial positions\n",
    "x_init = bunch.x.copy()\n",
    "xp_init = bunch.xp.copy()\n",
    "y_init = bunch.y.copy()\n",
    "yp_init = bunch.yp.copy()\n",
    "z_init = bunch.z.copy()\n",
    "dp_init = bunch.dp.copy()\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### create the maps:  insert space-charge element"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Start PIC init.:\n",
      "FFT, Open Boundary, Square Grid\n",
      "PyPIC Version 1.03\n",
      "Using PyFFTW\n",
      "PyPIC Version 1.03\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "../PyPIC/PyPIC_Scatter_Gather.py:70: FutureWarning: comparison to `None` will result in an elementwise object comparison in the future.\n",
      "  if xg!=None and xg!=None:\n"
     ]
    }
   ],
   "source": [
    "# longitudinal slicing of the bunch\n",
    "z_cut = np.max(np.abs(bunch_for_field.z))*1.2\n",
    "n_slices = 50\n",
    "slicer = UniformBinSlicer(n_slices = n_slices, z_cuts=(-z_cut, z_cut))\n",
    "\n",
    "# spacecharge object\n",
    "spacechargepic = FFT_OpenBoundary_SquareGrid(x_aper=bunch_for_field.sigma_x()*4, \n",
    "                                             y_aper=bunch_for_field.sigma_y()*4,\n",
    "                                             Dh=(bunch_for_field.sigma_x()+bunch_for_field.sigma_y())/2/10)\n",
    "spacecharge = TransverseSpaceCharge(L_interaction=1, slicer=slicer, pyPICsolver=spacechargepic)\n",
    "spacecharge.save_distributions_last_track = True\n",
    "spacecharge.save_potential_and_field = True\n",
    "\n",
    "# track the bunch through once to save the fields\n",
    "spacecharge.track(bunch_for_field)\n",
    "\n",
    "# create an electric field map object to store the field\n",
    "rescale_strength_by = 1.\n",
    "L_interaction = machine.circumference/len(machine.transverse_map)\n",
    "efieldmap = Transverse_Efield_map(xg = spacecharge.pyPICsolver.xg, yg = spacecharge.pyPICsolver.yg, \n",
    "                Ex=spacecharge.Ex_last_track, Ey=spacecharge.Ey_last_track, n_slices=n_slices, z_cut=z_cut, \n",
    "                L_interaction=L_interaction, flag_clean_slices = True, wrt_slice_centroid = False)\n",
    "\n",
    "# install ecloud field kick after each segment of the machine\n",
    "machine.install_after_each_transverse_segment(efieldmap)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### movie of charge density"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "slices = bunch_for_field.get_slices(spacecharge.slicer)\n",
    "show_movie = False\n",
    "if show_movie:\n",
    "    import time\n",
    "    n_frames = spacecharge.rho_last_track.shape[0]\n",
    "    plt.close(1)\n",
    "    plt.figure(1, figsize=(8,8))\n",
    "    vmax = np.max(spacecharge.rho_last_track[:])\n",
    "    vmin = np.min(spacecharge.rho_last_track[:])\n",
    "    for ii in xrange(n_frames-1, 0, -1):\n",
    "        plt.subplot2grid((10,1),(0,0), rowspan=3)\n",
    "        plt.plot(slices.z_centers, slices.n_macroparticles_per_slice/np.max(slices.n_macroparticles_per_slice))\n",
    "        plt.xlabel('z [m]');plt.ylabel('Long. profile')\n",
    "        plt.axvline(x = slices.z_centers[ii], color='r')\n",
    "        plt.subplot2grid((10,1),(4,0), rowspan=6)\n",
    "        plt.pcolormesh(spacecharge.pyPICsolver.xg*1e3, spacecharge.pyPICsolver.yg*1e3, \n",
    "                       spacecharge.rho_last_track[ii,:,:].T, vmax=vmax, vmin=vmin)\n",
    "        plt.xlabel('x [mm]');plt.ylabel('y [mm]')\n",
    "        plt.axis('equal')\n",
    "        plt.subplots_adjust(hspace=.5)\n",
    "        plt.draw()\n",
    "        #plt.show()\n",
    "        time.sleep(.2)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### track the particles"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "bunch: epsn_x= 2.52007264874e-06\n",
      "turn 127\n",
      "DONE\n",
      "bunch: epsn_x= 2.51824356368e-06\n"
     ]
    }
   ],
   "source": [
    "# particle positions for tune analysis\n",
    "x_i = np.empty((macroparticlenumber, n_turns))\n",
    "xp_i = np.empty((macroparticlenumber, n_turns))\n",
    "y_i = np.empty((macroparticlenumber, n_turns))\n",
    "yp_i = np.empty((macroparticlenumber, n_turns))\n",
    "\n",
    "bunch.update({'x': x_init, 'xp': xp_init, 'y': y_init, 'yp': yp_init})\n",
    "\n",
    "\n",
    "print 'bunch: epsn_x=',bunch.epsn_x()\n",
    "# track and store\n",
    "for i in range(n_turns):    \n",
    "    machine.track(bunch)\n",
    "    \n",
    "    sys.stdout.write('\\rturn %d'%i)\n",
    "    sys.stdout.flush()\n",
    "    \n",
    "    x_i[:,i] = bunch.x[:]\n",
    "    xp_i[:,i] = bunch.xp[:]\n",
    "    y_i[:,i] = bunch.y[:]\n",
    "    yp_i[:,i] = bunch.yp[:]\n",
    "print '\\nDONE'\n",
    "print 'bunch: epsn_x=',bunch.epsn_x()\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## plot the tune diagram"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "analysing particle spectra ... this may take some time.\n",
      "particle 1999"
     ]
    }
   ],
   "source": [
    "qx_i, qy_i, qx_centroid, qy_centroid = tune_analysis(bunch,  machine, x_i, xp_i, y_i, yp_i)\n",
    "plot_tune_spread(machine, qx_i, qy_i, qx_centroid, qy_centroid)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## plot efield"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<matplotlib.text.Text at 0x7f9299bffa90>"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "slice_2_plot = np.floor(0.5*slicer.n_slices)\n",
    "fig = plt.figure(6)\n",
    "fig.clf()\n",
    "ax = fig.gca(projection='3d')\n",
    "X = efieldmap.pic.xg\n",
    "Y = efieldmap.pic.yg\n",
    "X, Y = np.meshgrid(X, Y)\n",
    "surf = ax.plot_surface(X, Y, efieldmap.Ex[slice_2_plot,:,:].T, rstride=1, cstride=1, cmap=cm.jet,\n",
    "        linewidth=0.2, antialiased=True)\n",
    "# plt.plot(efieldmap.Ex[1]);\n",
    "plt.xlabel('x [m]')\n",
    "plt.ylabel('y [m]')\n",
    "ax.set_zlabel('Ex [V/m]')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 2",
   "language": "python",
   "name": "python2"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 2
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython2",
   "version": "2.7.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}
